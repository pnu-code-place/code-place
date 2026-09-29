from datetime import timedelta
from unittest import mock

from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from conf.models import JudgeServer
from judge.dispatcher import DispatcherBase, JudgeDispatcher
from judge.tasks import judge_task, cleanup_dead_judge_servers


class JudgeTaskObservabilityTest(SimpleTestCase):

    @mock.patch("judge.tasks.record_judge_task_outcome")
    @mock.patch("judge.tasks.JudgeDispatcher")
    @mock.patch("judge.tasks.User")
    @mock.patch("judge.tasks.Submission")
    def test_judge_task_records_success_outcome(self, submission_model, user_model, dispatcher, record_outcome):
        submission = mock.Mock(user_id=1, contest_id=None)
        submission_model.objects.get.return_value = submission
        user_model.objects.get.return_value = mock.Mock(is_disabled=False)
        judge_task.run(10, 20)

        dispatcher.assert_called_once_with(10, 20)
        dispatcher.return_value.judge.assert_called_once()
        record_outcome.assert_called_once_with("success", "practice")

    @mock.patch("judge.tasks.record_judge_task_outcome")
    @mock.patch("judge.tasks.JudgeDispatcher")
    @mock.patch("judge.tasks.User")
    @mock.patch("judge.tasks.Submission")
    def test_judge_task_records_disabled_user_outcome(self, submission_model, user_model, dispatcher, record_outcome):
        submission = mock.Mock(user_id=1, contest_id=7)
        submission_model.objects.get.return_value = submission
        user_model.objects.get.return_value = mock.Mock(is_disabled=True)
        judge_task.run(10, 20)

        dispatcher.assert_not_called()
        record_outcome.assert_called_once_with("user_disabled", "contest")


class CleanupDeadJudgeServersTest(TestCase):

    def test_cleanup_dead_judge_servers(self):
        """judge server dead 파드 제거 테스트"""
        JudgeServer.objects.create(
            hostname="dead_server",
            judger_version="1.0.4",
            cpu_core=4,
            memory_usage=80.3,
            cpu_usage=90.5,
            service_url="http://127.0.0.1",
            last_heartbeat=timezone.now() - timedelta(hours=13)
        )
        JudgeServer.objects.create(
            hostname="alive_server",
            judger_version="1.0.4",
            cpu_core=4,
            memory_usage=80.3,
            cpu_usage=90.5,
            service_url="http://127.0.0.1",
            last_heartbeat=timezone.now() - timedelta(hours=6)
        )

        deleted = cleanup_dead_judge_servers.run()

        self.assertEqual(deleted, 1)
        self.assertFalse(JudgeServer.objects.filter(hostname="dead_server").exists())
        self.assertTrue(JudgeServer.objects.filter(hostname="alive_server").exists())


class JudgeServerRoutingTest(TestCase):

    def setUp(self):
        with mock.patch.object(DispatcherBase, "__init__", lambda self: setattr(self, "token", "test_token")):
            self.dispatcher_base = DispatcherBase()

    def test_routing_with_pod_ip(self):
        """Pod IP가 있을 때 K8s Service 대신 개별 Pod IP로 라우팅되는지 검증"""
        server = mock.Mock(
            hostname="judge-pod-abc",
            ip="10.42.1.248",
            service_url="http://judge-server:8080",
        )
        judge_url = self.dispatcher_base._get_target_url(server, "/judge")
        spj_url = self.dispatcher_base._get_target_url(server, "compile_spj")

        self.assertEqual(judge_url, "http://10.42.1.248:8080/judge")
        self.assertEqual(spj_url, "http://10.42.1.248:8080/compile_spj")

    def test_routing_preserves_custom_port(self):
        """service_url에 명시된 포트 번호가 Pod IP URL에도 유지되는지 검증"""
        server = mock.Mock(
            hostname="judge-pod-abc",
            ip="10.42.1.248",
            service_url="http://judge-server:9090",
        )
        url = self.dispatcher_base._get_target_url(server, "/judge")
        self.assertEqual(url, "http://10.42.1.248:9090/judge")

    def test_routing_fallback_when_ip_is_none(self):
        """Pod IP가 None일 때 기존 service_url로 정상 fallback 되는지 검증"""
        server = mock.Mock(
            hostname="legacy-judge",
            ip=None,
            service_url="http://judge-server:8080",
        )
        judge_url = self.dispatcher_base._get_target_url(server, "/judge")
        self.assertEqual(judge_url, "http://judge-server:8080/judge")

    def test_routing_default_port_when_no_port_in_service_url(self):
        """service_url에 포트가 없을 때 기본 포트 8080이 사용되는지 검증"""
        server = mock.Mock(
            hostname="judge-pod-abc",
            ip="10.42.2.100",
            service_url="http://judge-server",
        )
        judge_url = self.dispatcher_base._get_target_url(server, "/judge")
        self.assertEqual(judge_url, "http://10.42.2.100:8080/judge")

    @mock.patch("judge.dispatcher.Submission")
    @mock.patch("judge.dispatcher.Problem")
    @mock.patch("judge.dispatcher.ChooseJudgeServer")
    def test_judge_dispatcher_calls_pod_ip_url(self, mock_choose_server, mock_problem, mock_submission):
        """JudgeDispatcher.judge 실행 시 Pod IP 직통 URL로 HTTP 요청이 전송되는지 검증"""
        mock_submission.objects.get.return_value = mock.Mock(
            id=123, contest_id=None, info=None, result=None, language="C", code="int main() {}"
        )
        mock_problem.objects.get.return_value = mock.Mock(
            id=456, test_case_id="test_case_1", time_limit=1000, memory_limit=128,
            spj=False, spj_version=None, spj_code=None, io_mode={"io_mode": "standard"},
            rule_type="ACM", template={}
        )
        server = mock.Mock(
            hostname="judge-server-pod-xyz",
            ip="10.42.3.15",
            service_url="http://judge-server:8080",
            task_number=1,
        )
        mock_choose_server.return_value.__enter__.return_value = server
        mock_choose_server.return_value.__exit__.return_value = None

        dispatcher = JudgeDispatcher(submission_id=123, problem_id=456)
        with mock.patch.object(dispatcher, "_request", return_value={"err": None, "data": []}) as mock_req:
            with mock.patch.object(dispatcher, "_compute_statistic_info"):
                with mock.patch.object(dispatcher, "update_problem_status"):
                    dispatcher.judge()
                    mock_req.assert_called_once()
                    call_args, _ = mock_req.call_args
                    self.assertEqual(call_args[0], "http://10.42.3.15:8080/judge")

    @mock.patch("judge.dispatcher.requests.post")
    def test_request_timeout(self, mock_post):
        """_request 호출 시 connect 5초, read 300초(5분) 타임아웃이 적용되는지 검증"""
        mock_resp = mock.Mock(status_code=200)
        mock_resp.json.return_value = {"err": None, "data": "ok"}
        mock_post.return_value = mock_resp

        self.dispatcher_base._request("http://10.42.1.100:8080/judge", data={"test": 1})
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs.get("timeout"), (5, 300))


