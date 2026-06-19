import celery
import logging

from account.models import User
from utils.shortcuts import CELERY_TASK_ARGS
from utils.observability_tracing import get_tracer
from utils.observability_metrics import JUDGE_TASK_OUTCOME_TOTAL
from submission.models import Submission
from judge.dispatcher import JudgeDispatcher

logger = logging.getLogger(__name__)
tracer = get_tracer(__name__)


def _record_judge_task_outcome(status, scope):
    JUDGE_TASK_OUTCOME_TOTAL.labels(status=status, scope=scope).inc()


@celery.shared_task(**CELERY_TASK_ARGS())
def judge_task(submission_id, problem_id):
    with tracer.start_as_current_span("judge_task") as span:
        span.set_attribute("codeplace.submission_id", submission_id)
        span.set_attribute("codeplace.problem_id", problem_id)
        scope = "unknown"
        try:
            submission = Submission.objects.get(id=submission_id)
            scope = "contest" if submission.contest_id else "practice"
        except Submission.DoesNotExist:
            _record_judge_task_outcome("submission_missing", scope)
            logger.exception("Judge task submission does not exist: %s", submission_id)
            raise

        try:
            user = User.objects.get(id=submission.user_id)
            if user.is_disabled:
                span.set_attribute("codeplace.judge.skipped", "user_disabled")
                _record_judge_task_outcome("user_disabled", scope)
                return

            JudgeDispatcher(submission_id, problem_id).judge()
        except User.DoesNotExist:
            _record_judge_task_outcome("user_missing", scope)
            logger.exception("Judge task user does not exist for submission %s", submission_id)
            raise
        except Exception:
            _record_judge_task_outcome("error", scope)
            logger.exception("Judge task failed for submission %s", submission_id)
            raise
        else:
            _record_judge_task_outcome("success", scope)
