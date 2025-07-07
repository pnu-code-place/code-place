import celery

from account.models import User
from utils.shortcuts import CELERY_TASK_ARGS
from submission.models import Submission
from judge.dispatcher import JudgeDispatcher


@celery.shared_task(**CELERY_TASK_ARGS())
def judge_task(submission_id, problem_id):
    uid = Submission.objects.get(id=submission_id).user_id
    if User.objects.get(id=uid).is_disabled:
        return
    JudgeDispatcher(submission_id, problem_id).judge()
