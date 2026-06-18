import celery
from opentelemetry import trace

from account.models import User
from utils.shortcuts import CELERY_TASK_ARGS
from submission.models import Submission
from judge.dispatcher import JudgeDispatcher

tracer = trace.get_tracer(__name__)


@celery.shared_task(**CELERY_TASK_ARGS())
def judge_task(submission_id, problem_id):
    with tracer.start_as_current_span("judge_task") as span:
        span.set_attribute("codeplace.submission_id", submission_id)
        span.set_attribute("codeplace.problem_id", problem_id)
        uid = Submission.objects.get(id=submission_id).user_id
        if User.objects.get(id=uid).is_disabled:
            span.set_attribute("codeplace.judge.skipped", "user_disabled")
            return
        JudgeDispatcher(submission_id, problem_id).judge()
