from unittest import mock

from django.test import SimpleTestCase

from judge.tasks import judge_task


class JudgeTaskObservabilityTest(SimpleTestCase):

    @mock.patch("judge.tasks.JUDGE_TASK_OUTCOME_TOTAL")
    @mock.patch("judge.tasks.JudgeDispatcher")
    @mock.patch("judge.tasks.User")
    @mock.patch("judge.tasks.Submission")
    def test_judge_task_records_success_outcome(self, submission_model, user_model, dispatcher, outcome_total):
        submission = mock.Mock(user_id=1, contest_id=None)
        submission_model.objects.get.return_value = submission
        user_model.objects.get.return_value = mock.Mock(is_disabled=False)
        labels = mock.Mock()
        outcome_total.labels.return_value = labels

        judge_task.run(10, 20)

        dispatcher.assert_called_once_with(10, 20)
        dispatcher.return_value.judge.assert_called_once()
        outcome_total.labels.assert_called_once_with(status="success", scope="practice")
        labels.inc.assert_called_once()

    @mock.patch("judge.tasks.JUDGE_TASK_OUTCOME_TOTAL")
    @mock.patch("judge.tasks.JudgeDispatcher")
    @mock.patch("judge.tasks.User")
    @mock.patch("judge.tasks.Submission")
    def test_judge_task_records_disabled_user_outcome(self, submission_model, user_model, dispatcher, outcome_total):
        submission = mock.Mock(user_id=1, contest_id=7)
        submission_model.objects.get.return_value = submission
        user_model.objects.get.return_value = mock.Mock(is_disabled=True)
        labels = mock.Mock()
        outcome_total.labels.return_value = labels

        judge_task.run(10, 20)

        dispatcher.assert_not_called()
        outcome_total.labels.assert_called_once_with(status="user_disabled", scope="contest")
        labels.inc.assert_called_once()
