import copy
from types import SimpleNamespace
from unittest import mock

from django.core.cache import cache
from django.test import SimpleTestCase
from django.utils import timezone
from datetime import timedelta

from contest.models import Contest
from contest.tests import DEFAULT_CONTEST_DATA
from judge.sample_runner import SampleRunError, SampleRunner
from problem.tests import DEFAULT_PROBLEM_DATA, ProblemCreateTestBase
from submission.models import Submission
from utils.api.tests import APITestCase


class SampleRunAPITest(APITestCase):
    def setUp(self):
        self.create_school_fixtures(1, "Test", 1, "Test")
        self.admin = self.create_super_admin()
        self.user = self.create_user(email="runner@test.com", username="runner", password="test1234!")
        self.problem = ProblemCreateTestBase.add_problem(DEFAULT_PROBLEM_DATA, self.admin)
        self.url = self.reverse("sample_run_api")
        self.data = {"problem_id": self.problem.id, "language": "C++", "code": "  int main() {}\n"}
        bucket = mock.patch("submission.views.oj.TokenBucket.consume", return_value=(True, 0))
        bucket.start()
        self.addCleanup(bucket.stop)
        runner = mock.patch("submission.views.oj.SampleRunner")
        self.runner = runner.start()
        self.addCleanup(runner.stop)
        self.runner.return_value.run.return_value = {"timeLimit": 1000, "memoryLimit": 256, "cases": []}
        self.lock_key = f"sample-run-active:{self.user.id}"
        cache.delete(self.lock_key)
        self.addCleanup(cache.delete, self.lock_key)

    def test_run_does_not_create_submission_or_change_statistics(self):
        profile = self.user.userprofile
        before = (profile.submission_number, profile.accepted_number, copy.deepcopy(profile.acm_problems_status))
        response = self.client.post(self.url, self.data)
        self.assertSuccess(response)
        self.runner.assert_called_once()
        problem, language, code = self.runner.call_args.args
        self.assertEqual(problem.id, self.problem.id)
        self.assertEqual(problem.samples, self.problem.samples)
        self.assertEqual((language, code), ("C++", self.data["code"]))
        self.assertFalse(Submission.objects.exists())
        profile.refresh_from_db()
        self.problem.refresh_from_db()
        self.assertEqual(before, (profile.submission_number, profile.accepted_number, profile.acm_problems_status))
        self.assertEqual(self.problem.submission_number, 0)
        self.assertEqual(self.problem.accepted_number, 0)
        self.assertIsNone(cache.get(self.lock_key))

    def test_anonymous_user_cannot_run(self):
        self.client.logout()
        self.assertEqual(self.client.post(self.url, self.data).status_code, 401)
        self.runner.assert_not_called()

    def test_hidden_problem_cannot_run(self):
        self.problem.visible = False
        self.problem.save(update_fields=["visible"])
        self.assertFailed(self.client.post(self.url, self.data), "Problem not exist")
        self.runner.assert_not_called()

    def test_request_cannot_override_problem_samples(self):
        self.data["samples"] = [{"input": "forged", "output": "forged"}]
        self.data["test_case_id"] = "PRIVATE_DO_NOT_USE"
        self.assertSuccess(self.client.post(self.url, self.data))
        self.assertEqual(self.runner.call_args.args[0].samples, self.problem.samples)

    def test_disabled_user_cannot_run(self):
        self.user.is_disabled = True
        self.user.save(update_fields=["is_disabled"])
        self.assertEqual(self.client.post(self.url, self.data).status_code, 403)
        self.runner.assert_not_called()

    def test_disallowed_language_cannot_run(self):
        self.problem.languages = ["C"]
        self.problem.save(update_fields=["languages"])
        self.assertFailed(self.client.post(self.url, self.data))
        self.runner.assert_not_called()

    def test_blank_code_cannot_run(self):
        self.data["code"] = " \n\t"
        self.assertFailed(self.client.post(self.url, self.data))
        self.runner.assert_not_called()

    def test_concurrent_run_is_rejected(self):
        cache.add(self.lock_key, True, timeout=90)
        self.assertEqual(self.client.post(self.url, self.data).status_code, 429)
        self.runner.assert_not_called()
        self.assertTrue(cache.get(self.lock_key))

    def test_throttled_run_is_rejected(self):
        with mock.patch("submission.views.oj.TokenBucket.consume", return_value=(False, 5)):
            self.assertEqual(self.client.post(self.url, self.data).status_code, 429)
        self.runner.assert_not_called()

    def test_server_failure_releases_lock_and_allows_retry(self):
        self.runner.return_value.run.side_effect = SampleRunError("서버 응답 없음")
        self.assertEqual(self.client.post(self.url, self.data).status_code, 503)
        self.assertIsNone(cache.get(self.lock_key))
        self.runner.return_value.run.side_effect = None
        self.assertSuccess(self.client.post(self.url, self.data))

    def test_contest_problem_requires_correct_contest_and_password(self):
        data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        data.update(created_by=self.admin)
        contest = Contest.objects.create(**data)
        self.problem.contest = contest
        self.problem.save(update_fields=["contest"])
        self.assertFailed(self.client.post(self.url, self.data), "Problem not exist")
        self.data["contest_id"] = contest.id
        self.assertFailed(self.client.post(self.url, self.data), "Wrong password or password expired")
        self.runner.assert_not_called()

    def _make_running_contest(self, **kwargs):
        data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        data.update(created_by=self.admin, password="", start_time=timezone.now() - timedelta(hours=1),
                    end_time=timezone.now() + timedelta(hours=1), **kwargs)
        contest = Contest.objects.create(**data)
        self.problem.contest = contest
        self.problem.save(update_fields=["contest"])
        self.data["contest_id"] = contest.id
        return contest

    def test_contest_sample_run_is_off_by_default(self):
        contest = self._make_running_contest()
        self.assertFalse(contest.sample_run_enabled)
        self.assertFailed(self.client.post(self.url, self.data), "이 대회에서는 예제 실행을 사용할 수 없습니다.")
        self.runner.assert_not_called()

    def test_contest_sample_run_allowed_when_enabled(self):
        self._make_running_contest(sample_run_enabled=True)
        self.assertSuccess(self.client.post(self.url, self.data))
        self.runner.assert_called_once()

    def test_lock_outlives_request_timeout(self):
        from submission.views.oj import SampleRunAPI
        self.assertGreater(SampleRunAPI.LOCK_TIMEOUT, SampleRunner.REQUEST_TIMEOUT)
        with mock.patch("submission.views.oj.cache.add", wraps=cache.add) as add:
            self.assertSuccess(self.client.post(self.url, self.data))
        self.assertEqual(add.call_args.kwargs["timeout"], SampleRunAPI.LOCK_TIMEOUT)

    def test_future_contest_cannot_run(self):
        data = copy.deepcopy(DEFAULT_CONTEST_DATA)
        data.update(created_by=self.admin, password="", start_time=timezone.now() + timedelta(hours=1),
                    end_time=timezone.now() + timedelta(hours=2))
        contest = Contest.objects.create(**data)
        self.problem.contest = contest
        self.problem.save(update_fields=["contest"])
        self.data["contest_id"] = contest.id
        self.assertFailed(self.client.post(self.url, self.data), "Contest has not started yet.")
        self.runner.assert_not_called()


class SampleRunThrottleConfigTest(SimpleTestCase):
    def test_uses_dedicated_sample_run_option(self):
        from submission.views.oj import SampleRunAPI, SubmissionAPI
        throttling = {"user": {"capacity": 20, "fill_rate": 0.03, "default_capacity": 10},
                      "sample_run": {"capacity": 5, "fill_rate": 0.2, "default_capacity": 5}}
        with mock.patch("submission.views.oj.SysOptions", SimpleNamespace(throttling=throttling)):
            self.assertEqual(SampleRunAPI().throttle_config(), throttling["sample_run"])
            self.assertEqual(SubmissionAPI().throttle_config(), throttling["user"])

    def test_falls_back_to_default_when_stored_option_lacks_key(self):
        from options.options import OptionDefaultValue
        from submission.views.oj import SampleRunAPI
        throttling = {"user": {"capacity": 20, "fill_rate": 0.03, "default_capacity": 10}}
        with mock.patch("submission.views.oj.SysOptions", SimpleNamespace(throttling=throttling)):
            config = SampleRunAPI().throttle_config()
        self.assertEqual(config, OptionDefaultValue.throttling["sample_run"])
        self.assertEqual((config["capacity"], config["fill_rate"]), (10, 0.1))


class SampleRunnerTest(SimpleTestCase):
    def setUp(self):
        self.problem = SimpleNamespace(
            samples=[{"input": "1 2\n", "output": "3\n"}, {"input": "2 3\n", "output": "5\n"}],
            time_limit=1000, memory_limit=128, template={}, spj=False,
            io_mode={"io_mode": "Standard IO"}, test_case_id="PRIVATE_DO_NOT_USE",
        )
        self.options = SimpleNamespace(languages=[
            {"name": "C++", "config": {"run": {"command": "main"}}},
            {"name": "Python3", "config": {"run": {"command": "python3"}}},
        ])
        patchers = [
            mock.patch("judge.sample_runner.SysOptions", self.options),
            mock.patch("judge.sample_runner.DispatcherBase.__init__", return_value=None),
            mock.patch("judge.sample_runner.ChooseJudgeServer"),
        ]
        for patcher in patchers:
            started = patcher.start()
            self.addCleanup(patcher.stop)
        self.server = started
        self.server.return_value.__enter__.return_value = SimpleNamespace(ip=None, service_url="http://judge:8080")
        self.runner = SampleRunner(self.problem, "C++", "int main() {}")
        self.response = {"err": None, "data": [
            {"test_case": "2", "result": -1, "output": "4\n", "cpu_time": 3, "memory": 2097152},
            {"test_case": "1", "result": 0, "output": "3\n", "cpu_time": 2, "memory": 1048576},
        ]}

    def run_with_response(self, response):
        with mock.patch.object(self.runner, "_request", return_value=response) as request:
            return self.runner.run(), request

    def test_only_samples_sent_and_results_ordered_and_units_converted(self):
        result, request = self.run_with_response(self.response)
        payload = request.call_args.kwargs["data"]
        self.assertEqual(payload["test_case"], self.problem.samples)
        self.assertNotIn("test_case_id", payload)
        self.assertNotIn("PRIVATE_DO_NOT_USE", str(payload))
        self.assertTrue(payload["output"])
        self.assertEqual([case["type"] for case in result["cases"]], ["accepted", "wrong_answer"])
        self.assertEqual(result["cases"][0]["output"], "3\n")
        self.assertEqual(result["cases"][0]["time"], 2)
        self.assertEqual(result["cases"][0]["memory"], 1024)
        self.assertEqual(result["cases"][1]["expected"], "5\n")

    def test_judge_request_uses_short_timeout(self):
        _, request = self.run_with_response(self.response)
        self.assertEqual(request.call_args.kwargs["timeout"], SampleRunner.REQUEST_TIMEOUT)
        self.assertEqual(SampleRunner.REQUEST_TIMEOUT, 60)

    def test_problem_template_is_applied(self):
        self.problem.template = {"C++": "//PREPEND BEGIN\nheader\n//PREPEND END\n//APPEND BEGIN\nfooter\n//APPEND END"}
        _, request = self.run_with_response(self.response)
        source = request.call_args.kwargs["data"]["src"]
        self.assertIn("header", source)
        self.assertIn("int main() {}", source)
        self.assertIn("footer", source)

    def test_compile_error_returned_without_inventing_cases(self):
        result, _ = self.run_with_response({"err": "CompileError", "data": "syntax error"})
        self.assertEqual(result["compileError"], "syntax error")
        self.assertEqual(result["cases"], [])

    def test_spj_uses_sample_input_and_problem_checker(self):
        self.problem.spj = True
        self.problem.spj_language = "C"
        self.problem.spj_version = "checker-version"
        self.problem.spj_code = "checker source"
        self.options.spj_languages = [{"name": "C", "spj": {"config": {"exe_name": "spj"}, "compile": {"src_name": "spj.c"}}}]
        _, request = self.run_with_response(self.response)
        payload = request.call_args.kwargs["data"]
        self.assertEqual(payload["test_case"], self.problem.samples)
        self.assertNotIn("test_case_id", payload)
        self.assertEqual(payload["spj_src"], "checker source")
        self.assertEqual(payload["spj_version"], "checker-version")

    def test_no_samples_does_not_call_judge(self):
        self.problem.samples = []
        result, request = self.run_with_response(None)
        self.assertEqual(result["cases"], [])
        request.assert_not_called()

    def test_unavailable_server_and_invalid_responses_fail(self):
        for response in (None, {"err": "JudgeClientError", "data": "private details"}, {"err": None, "data": []}):
            with self.subTest(response=response), self.assertRaises(SampleRunError):
                self.run_with_response(response)
        self.server.return_value.__enter__.return_value = None
        with self.assertRaises(SampleRunError):
            self.runner.run()

    def test_runtime_time_and_memory_results_keep_measured_values(self):
        for status, expected in ((1, "time_limit"), (2, "time_limit"), (3, "memory_limit"), (4, "runtime_error"), (5, "system_error")):
            with self.subTest(status=status):
                response = copy.deepcopy(self.response)
                response["data"][1].update(result=status, output="runtime diagnostic", cpu_time=1050, memory=150 * 1024 * 1024)
                result, _ = self.run_with_response(response)
                self.assertEqual(result["cases"][0]["type"], expected)
                self.assertEqual(result["cases"][0]["time"], 1050)
                self.assertEqual(result["cases"][0]["memory"], 150 * 1024)

    def test_large_output_is_bounded_and_flagged(self):
        self.response["data"][0]["output"] = "x" * (self.runner.OUTPUT_LIMIT + 1)
        result, _ = self.run_with_response(self.response)
        self.assertEqual(len(result["cases"][1]["output"]), self.runner.OUTPUT_LIMIT)
        self.assertTrue(result["cases"][1]["outputTruncated"])

    def test_infinite_print_output_limit_is_not_reported_as_runtime_error(self):
        self.runner.language = "Python3"
        for output, signal in (("1\n" * (self.runner.JUDGE_MIN_OUTPUT_LIMIT // 2), 0), ("", 25),
                               ("OSError: [Errno 27] File too large", 0)):
            with self.subTest(signal=signal, output_size=len(output)):
                response = copy.deepcopy(self.response)
                response["data"][1].update(result=4, output=output, signal=signal, exit_code=1)
                result, _ = self.run_with_response(response)
                case = result["cases"][0]
                self.assertEqual(case["type"], "output_limit")
                self.assertEqual(case["error"], "")
                self.assertEqual(case["output"], "")

    def test_time_and_memory_limits_have_no_error_message(self):
        for status in (1, 2, 3):
            with self.subTest(status=status):
                response = copy.deepcopy(self.response)
                response["data"][1].update(result=status, output="1\n" * 100)
                result, _ = self.run_with_response(response)
                self.assertEqual(result["cases"][0]["error"], "")

    def test_python_runtime_error_does_not_use_print_output_as_diagnostic(self):
        self.runner.language = "Python3"
        response = copy.deepcopy(self.response)
        response["data"][1].update(result=4, output="1\n" * 100, signal=11, exit_code=0)
        result, _ = self.run_with_response(response)
        self.assertEqual(result["cases"][0]["type"], "runtime_error")
        self.assertNotIn("1\n", result["cases"][0]["error"])
        traceback = "Traceback (most recent call last):\nZeroDivisionError: division by zero"
        response["data"][1]["output"] += traceback
        result, _ = self.run_with_response(response)
        self.assertEqual(result["cases"][0]["error"], traceback)
