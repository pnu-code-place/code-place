import celery

from account.models import User
from submission.models import Submission
from judge.dispatcher import JudgeDispatcher


@celery.shared_task(max_retries=0, time_limit=3600, soft_time_limit=3600)
def judge_task(submission_id, problem_id):
    uid = Submission.objects.get(id=submission_id).user_id
    if User.objects.get(id=uid).is_disabled:
        return
    JudgeDispatcher(submission_id, problem_id).judge()
