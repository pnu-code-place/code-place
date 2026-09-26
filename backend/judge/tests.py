from datetime import timedelta
from unittest import mock

from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from conf.models import JudgeServer
from contest.models import ContestRuleType
from judge.dispatcher import JudgeDispatcher
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


class ContestRankCacheRefreshTest(SimpleTestCase):

    @mock.patch("judge.dispatcher.refresh_public_rank_cache")
    @mock.patch("judge.dispatcher.transaction.on_commit")
    @mock.patch("judge.dispatcher.ACMContestRank")
    def test_real_time_rank_cache_is_refreshed_after_commit(self, rank_model, on_commit, refresh_rank_cache):
        dispatcher = JudgeDispatcher.__new__(JudgeDispatcher)
        dispatcher.contest = mock.Mock(id=42, rule_type=ContestRuleType.ACM, real_time_rank=True)
        dispatcher.submission = mock.Mock(user_id=7)
        dispatcher._update_acm_contest_rank = mock.Mock()
        rank = mock.Mock()
        rank_model.objects.select_for_update.return_value.get.return_value = rank

        dispatcher.update_contest_rank()

        dispatcher._update_acm_contest_rank.assert_called_once_with(rank)
        refresh_rank_cache.assert_not_called()
        on_commit.assert_called_once()

        callback = on_commit.call_args.args[0]
        callback()

        refresh_rank_cache.assert_called_once_with(42, force=True)
