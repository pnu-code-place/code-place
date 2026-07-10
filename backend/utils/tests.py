import json
import logging
import os
import pickle
from unittest.mock import patch, mock_open, MagicMock
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.core.cache import cache
from prometheus_client.core import GaugeMetricFamily

from utils.json_logging import CodePlaceJsonFormatter
from utils.api import APIView
from utils.observability_metrics import CodePlaceCollector
from utils import observability_tracing
from utils.testcase_cache import TestCaseCacheManager
from utils.throttling import TokenBucket


class TokenBucketTest(SimpleTestCase):

    def test_reads_raw_byte_values(self):
        redis_conn = MagicMock()
        redis_conn.hget.side_effect = [b"7.0"]

        bucket = TokenBucket("1", capacity=10, fill_rate=1, default_capacity=10, redis_conn=redis_conn)

        self.assertEqual(bucket._last_capacity, 7.0)

    def test_reads_pickled_byte_values_from_django_redis_hash(self):
        redis_conn = MagicMock()
        redis_conn.hget.side_effect = [pickle.dumps(7.0)]

        bucket = TokenBucket("1", capacity=10, fill_rate=1, default_capacity=10, redis_conn=redis_conn)

        self.assertEqual(bucket._last_capacity, 7.0)


class APIViewStatusCodeTest(SimpleTestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_server_exception_returns_http_500_with_existing_json_body(self):

        class BrokenAPIView(APIView):

            def get(self, request):
                raise RuntimeError("boom")

        response = BrokenAPIView.as_view()(self.factory.get("/"))

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data, {"error": "server-error", "data": "server error"})

    def test_business_error_returns_http_400(self):

        class BusinessErrorAPIView(APIView):

            def get(self, request):
                return self.error(err="problem-not-found", msg="Problem not exist")

        response = BusinessErrorAPIView.as_view()(self.factory.get("/"))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"error": "problem-not-found", "data": "Problem not exist"})


class CodePlaceCollectorTest(SimpleTestCase):

    def _samples_by_metric(self, metrics):
        return {metric.name: metric.samples for metric in metrics}

    def test_celery_broker_queue_length_is_collected_from_redis(self):
        broker_client = MagicMock()
        broker_client.llen.return_value = 7
        with patch.object(CodePlaceCollector, "_celery_broker_client", return_value=broker_client):
            samples = self._samples_by_metric([CodePlaceCollector()._celery_broker_queue_length()])

        broker_client.llen.assert_called_once_with("celery")
        self.assertEqual(samples["codeplace_celery_broker_queue_length"][0].value, 7)

    @override_settings(REDIS_USE_SENTINEL=False, CELERY_BROKER_URL="redis://127.0.0.1:6380/4")
    def test_celery_broker_client_uses_celery_broker_url(self):
        with patch("utils.observability_metrics.Redis.from_url") as from_url:
            CodePlaceCollector._celery_broker_client()

        from_url.assert_called_once_with("redis://127.0.0.1:6380/4")

    @override_settings(
        REDIS_USE_SENTINEL=True,
        REDIS_SENTINEL_HOSTS=[("redis-sentinel", 26379)],
        REDIS_SENTINEL_MASTER_NAME="mymaster",
    )
    def test_celery_broker_client_uses_sentinel_broker_db(self):
        sentinel = MagicMock()
        with patch("utils.observability_metrics.Sentinel", return_value=sentinel) as sentinel_cls:
            CodePlaceCollector._celery_broker_client()

        sentinel_cls.assert_called_once_with([("redis-sentinel", 26379)], socket_timeout=1)
        sentinel.master_for.assert_called_once_with("mymaster", db=4, socket_timeout=1)


class CodePlaceMetricsEndpointTest(SimpleTestCase):

    def test_metrics_endpoint_exposes_django_and_codeplace_metrics(self):
        waiting_queue_metric = GaugeMetricFamily(
            "codeplace_waiting_queue_length",
            "Number of submissions waiting because no judge-server was available.",
        )
        waiting_queue_metric.add_metric([], 0)
        broker_queue_metric = GaugeMetricFamily(
            "codeplace_celery_broker_queue_length",
            "Number of Celery tasks waiting in the Redis broker default queue.",
        )
        broker_queue_metric.add_metric([], 0)
        with patch.object(CodePlaceCollector, "_waiting_queue_length", return_value=waiting_queue_metric), \
                patch.object(CodePlaceCollector, "_celery_broker_queue_length", return_value=broker_queue_metric):
            response = self.client.get("/metrics")

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("django_http_requests_total_by_method_total", body)
        self.assertIn("codeplace_waiting_queue_length", body)
        self.assertIn("codeplace_celery_broker_queue_length", body)


class ObservabilityTracingTest(SimpleTestCase):

    def tearDown(self):
        observability_tracing._OTEL_CONFIGURED = False

    def test_configure_opentelemetry_is_idempotent(self):
        observability_tracing._OTEL_CONFIGURED = True
        real_import = __import__

        def fail_import(name, *args, **kwargs):
            if name == "opentelemetry":
                raise AssertionError("OpenTelemetry should not be imported again")
            return real_import(name, *args, **kwargs)

        with patch("utils.observability_tracing.get_env", return_value="1"), \
                patch("builtins.__import__", side_effect=fail_import):
            observability_tracing.configure_opentelemetry("codeplace-test")


class CodePlaceJsonFormatterTest(SimpleTestCase):

    def test_preserves_status_code_and_redacts_sensitive_fields(self):
        record = logging.LogRecord(
            name="codeplace.request",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="request completed",
            args=(),
            exc_info=None,
        )
        record.status_code = 500
        record.request_id = "request-1"
        record.token = "secret-token"
        record.source_code = "print('secret')"

        payload = json.loads(CodePlaceJsonFormatter().format(record))

        self.assertEqual(payload["status_code"], 500)
        self.assertEqual(payload["request_id"], "request-1")
        self.assertNotIn("token", payload)
        self.assertNotIn("source_code", payload)

    def test_includes_trace_context_when_available(self):
        record = logging.LogRecord(
            name="codeplace.request",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="request completed",
            args=(),
            exc_info=None,
        )

        with patch("utils.json_logging.get_current_trace_context", return_value={
            "trace_id": "0" * 31 + "1",
            "span_id": "0" * 15 + "2",
        }):
            payload = json.loads(CodePlaceJsonFormatter().format(record))

        self.assertEqual(payload["trace_id"], "0" * 31 + "1")
        self.assertEqual(payload["span_id"], "0" * 15 + "2")

    def test_redacts_nested_sensitive_fields(self):
        formatter = CodePlaceJsonFormatter()
        payload = {
            "status_code": 200,
            "data": {
                "password": "secret",
                "submission": {
                    "code": "print('secret')",
                    "language": "Python3",
                },
            },
        }

        redacted = formatter._redact(payload)

        self.assertEqual(redacted["status_code"], 200)
        self.assertEqual(redacted["data"]["password"], "[REDACTED]")
        self.assertEqual(redacted["data"]["submission"]["code"], "[REDACTED]")
        self.assertEqual(redacted["data"]["submission"]["language"], "Python3")


class TestTestCaseCacheManager(TestCase):

    def setUp(self):
        """각 테스트 전에 캐시 클리어"""
        cache.clear()

    def tearDown(self):
        """각 테스트 후에 캐시 클리어"""
        cache.clear()

    def test_get_cache_key(self):
        """_get_cache_key 메서드 테스트"""
        cache_key = TestCaseCacheManager._get_cache_key("problem1", 1)
        expected_key = "testcase:problem1:1"
        self.assertEqual(cache_key, expected_key)

        cache_key2 = TestCaseCacheManager._get_cache_key("algorithm", 99)
        expected_key2 = "testcase:algorithm:99"
        self.assertEqual(cache_key2, expected_key2)

    def test_get_testcase_from_cache_string_data(self):
        """캐시에서 문자열 데이터를 가져오는 테스트"""
        testcase_dir = "problem1"
        testcase_idx = 1
        cache_key = TestCaseCacheManager._get_cache_key(testcase_dir, testcase_idx)

        test_data = {"input": "test input", "output": "test output"}
        cache.set(cache_key, json.dumps(test_data))

        result = TestCaseCacheManager.get_testcase(testcase_dir, testcase_idx)
        self.assertEqual(result, test_data)

    def test_get_testcase_from_cache_dict_data(self):
        """캐시에서 딕셔너리 데이터를 가져오는 테스트"""
        testcase_dir = "problem2"
        testcase_idx = 2
        cache_key = TestCaseCacheManager._get_cache_key(testcase_dir, testcase_idx)

        test_data = {"input": "dict input", "output": "dict output"}
        cache.set(cache_key, test_data)

        result = TestCaseCacheManager.get_testcase(testcase_dir, testcase_idx)
        self.assertEqual(result, test_data)

    @patch.object(TestCaseCacheManager, '_read_testcase_from_file')
    def test_get_testcase_cache_miss_with_file_data(self, mock_read_file):
        """캐시 미스 시 파일에서 읽어 캐시에 저장하는 테스트"""
        testcase_dir = "problem3"
        testcase_idx = 3
        cache_key = TestCaseCacheManager._get_cache_key(testcase_dir, testcase_idx)

        file_data = {"input": "file input", "output": "file output"}
        mock_read_file.return_value = file_data

        result = TestCaseCacheManager.get_testcase(testcase_dir, testcase_idx)

        self.assertEqual(result, file_data)
        mock_read_file.assert_called_once_with(testcase_dir, testcase_idx)

        cached_data = cache.get(cache_key)
        self.assertEqual(json.loads(cached_data), file_data)

    @patch.object(TestCaseCacheManager, '_read_testcase_from_file')
    def test_get_testcase_cache_miss_no_file_data(self, mock_read_file):
        """캐시 미스이고 파일에서도 데이터를 읽지 못하는 테스트"""
        testcase_dir = "problem4"
        testcase_idx = 4

        mock_read_file.return_value = None

        result = TestCaseCacheManager.get_testcase(testcase_dir, testcase_idx)

        self.assertIsNone(result)
        mock_read_file.assert_called_once_with(testcase_dir, testcase_idx)

    @patch('utils.testcase_cache.logger')    # 실제 모듈 경로에 맞게 수정
    def test_read_testcase_invalid_directory_name(self, mock_logger):
        """잘못된 디렉토리 이름 검증 테스트"""
        result = TestCaseCacheManager._read_testcase_from_file("problem-1", 1)

        self.assertIsNone(result)
        mock_logger.error.assert_called_with(
            "Invalid testcase directory name. Only alphanumeric characters are allowed.")

    @patch('utils.testcase_cache.logger')    # 실제 모듈 경로에 맞게 수정
    def test_read_testcase_invalid_index_negative(self, mock_logger):
        """음수 인덱스 검증 테스트"""
        result = TestCaseCacheManager._read_testcase_from_file("problem1", -1)

        self.assertIsNone(result)
        mock_logger.error.assert_called_with("Invalid testcase index. It must be a non-negative integer.")

    @patch('utils.testcase_cache.logger')    # 실제 모듈 경로에 맞게 수정
    def test_read_testcase_invalid_index_non_integer(self, mock_logger):
        """정수가 아닌 인덱스 검증 테스트"""
        result = TestCaseCacheManager._read_testcase_from_file("problem1", "invalid")

        self.assertIsNone(result)
        mock_logger.error.assert_called_with("Invalid testcase index. It must be a non-negative integer.")

    @override_settings(TEST_CASE_DIR="/test/cases")
    @patch('os.path.abspath')
    @patch('utils.testcase_cache.logger')    # 실제 모듈 경로에 맞게 수정
    def test_read_testcase_path_traversal_attack(self, mock_logger, mock_abspath):
        """경로 순회 공격 방지 테스트"""
        # abspath 모킹 - 악성 경로로 설정
        mock_abspath.side_effect = [
            "/test/cases",    # base_dir
            "/etc/passwd",    # input_file_path (악성)
            "/test/cases/problem1/1.out"    # output_file_path
        ]

        result = TestCaseCacheManager._read_testcase_from_file("problem1", 1)

        self.assertIsNone(result)
        mock_logger.error.assert_called_with("Attempt to access files outside the test case directory.")

    @override_settings(TEST_CASE_DIR="/test/cases")
    @patch("builtins.open", new_callable=mock_open)
    @patch('os.path.abspath')
    def test_read_testcase_from_file_success(self, mock_abspath, mock_file):
        """파일 읽기 성공 테스트"""
        mock_abspath.side_effect = [
            "/test/cases",    # base_dir
            "/test/cases/problem5/5.in",    # input_file_path
            "/test/cases/problem5/5.out"    # output_file_path
        ]

        mock_file.side_effect = [
            mock_open(read_data="input content").return_value,
            mock_open(read_data="output content").return_value
        ]

        result = TestCaseCacheManager._read_testcase_from_file("problem5", 5)

        expected_result = {"input": "input content", "output": "output content"}
        self.assertEqual(result, expected_result)

        # 파일이 두 번 열렸는지 확인
        self.assertEqual(mock_file.call_count, 2)

    @override_settings(TEST_CASE_DIR="/test/cases")
    @patch("builtins.open", side_effect=FileNotFoundError("File not found"))
    @patch('os.path.abspath')
    @patch('utils.testcase_cache.logger')    # 실제 모듈 경로에 맞게 수정
    def test_read_testcase_from_file_not_found(self, mock_logger, mock_abspath, mock_open_file):
        """파일이 존재하지 않는 경우 테스트"""
        mock_abspath.side_effect = [
            "/test/cases",    # base_dir
            "/test/cases/problem6/6.in",    # input_file_path
            "/test/cases/problem6/6.out"    # output_file_path
        ]

        result = TestCaseCacheManager._read_testcase_from_file("problem6", 6)

        self.assertIsNone(result)
        mock_logger.error.assert_called()
        error_call_args = mock_logger.error.call_args[0][0]
        self.assertIn("Failed to read testcase file", error_call_args)

    @override_settings(TEST_CASE_DIR="/test/cases")
    @patch("builtins.open", side_effect=IOError("IO Error"))
    @patch('os.path.abspath')
    @patch('utils.testcase_cache.logger')    # 실제 모듈 경로에 맞게 수정
    def test_read_testcase_from_file_io_error(self, mock_logger, mock_abspath, mock_open_file):
        """IO 에러 발생 시 테스트"""
        mock_abspath.side_effect = [
            "/test/cases",    # base_dir
            "/test/cases/problem7/7.in",    # input_file_path
            "/test/cases/problem7/7.out"    # output_file_path
        ]

        result = TestCaseCacheManager._read_testcase_from_file("problem7", 7)

        self.assertIsNone(result)
        mock_logger.error.assert_called()
        error_call_args = mock_logger.error.call_args[0][0]
        self.assertIn("Failed to read testcase file", error_call_args)

    def test_cache_timeout_setting(self):
        """캐시 타임아웃 설정 테스트"""
        self.assertEqual(TestCaseCacheManager.DEFAULT_TIMEOUT, 3600)    # 1시간

    def test_cache_prefix_setting(self):
        """캐시 프리픽스 설정 테스트"""
        self.assertEqual(TestCaseCacheManager.CACHE_PREFIX, "testcase")

    @patch.object(TestCaseCacheManager, '_read_testcase_from_file')
    def test_integration_flow(self, mock_read_file):
        """전체 플로우 통합 테스트"""
        testcase_dir = "integration"
        testcase_idx = 1
        file_data = {"input": "integration input", "output": "integration output"}
        mock_read_file.return_value = file_data

        # 첫 번째 호출 - 캐시 미스, 파일에서 읽음
        result1 = TestCaseCacheManager.get_testcase(testcase_dir, testcase_idx)
        self.assertEqual(result1, file_data)
        mock_read_file.assert_called_once()

        # 두 번째 호출 - 캐시 히트, 파일 읽기 없음
        result2 = TestCaseCacheManager.get_testcase(testcase_dir, testcase_idx)
        self.assertEqual(result2, file_data)
        # mock_read_file은 한 번만 호출되어야 함
        self.assertEqual(mock_read_file.call_count, 1)

    @override_settings(TEST_CASE_DIR="/test/cases")
    @patch('os.path.join')
    def test_os_path_join_usage(self, mock_path_join):
        """os.path.join 사용 확인 테스트"""
        mock_path_join.side_effect = lambda *args: "/".join(args)

        with patch('os.path.abspath') as mock_abspath:
            mock_abspath.side_effect = [
                "/test/cases",    # base_dir
                "/test/cases/test/1.in",    # input_file_path
                "/test/cases/test/1.out"    # output_file_path
            ]

            with patch("builtins.open", side_effect=FileNotFoundError()):
                with patch('logging.getLogger'):
                    TestCaseCacheManager._read_testcase_from_file("test", 1)

            self.assertTrue(mock_path_join.called)
            # 최소 2번은 호출되어야 함 (input, output 파일 경로)
            self.assertGreaterEqual(mock_path_join.call_count, 2)
