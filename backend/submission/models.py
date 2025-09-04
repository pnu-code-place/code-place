from account.models import UserProfile
from contest.models import Contest
from django.db import models
from problem.models import Problem
from utils.constants import ContestStatus
from utils.models import JSONField
from utils.shortcuts import rand_str


class JudgeStatus:
    COMPILE_ERROR = -2
    WRONG_ANSWER = -1
    ACCEPTED = 0
    CPU_TIME_LIMIT_EXCEEDED = 1
    REAL_TIME_LIMIT_EXCEEDED = 2
    MEMORY_LIMIT_EXCEEDED = 3
    RUNTIME_ERROR = 4
    SYSTEM_ERROR = 5
    PENDING = 6
    JUDGING = 7
    PARTIALLY_ACCEPTED = 8


class Submission(models.Model):
    id = models.TextField(default=rand_str, primary_key=True, db_index=True)
    contest = models.ForeignKey(Contest, null=True, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    judge_start_time = models.DateTimeField(null=True)
    judge_end_time = models.DateTimeField(null=True)
    user_id = models.IntegerField(db_index=True)
    username = models.TextField()
    code = models.TextField()
    result = models.IntegerField(db_index=True, default=JudgeStatus.PENDING)
    # 从JudgeServer返回的判题详情
    info = JSONField(default=dict)
    language = models.TextField()
    shared = models.BooleanField(default=False)
    # 存储该提交所用时间和内存值，方便提交列表显示
    # {time_cost: "", memory_cost: "", err_info: "", score: 0}
    statistic_info = JSONField(default=dict)
    ip = models.TextField(null=True)
    # 최초로 실패한 테스트 케이스의 인덱스, 연습 문제에서 틀린 테스트케이스를 보여주기 위해 사용됩니다.
    first_failed_tc_idx = models.IntegerField(null=True, default=None)

    def check_user_permission(self, user, check_share=True):
        if (
            self.user_id == user.id
            or user.is_super_admin()
            or user.can_mgmt_all_problem()
            or self.problem.created_by_id == user.id
        ):
            return True

        if check_share:
            if self.contest and self.contest.status != ContestStatus.CONTEST_ENDED:
                return False
            if self.problem.share_submission or self.shared:
                return True
        return False

    class Meta:
        db_table = "submission"
        ordering = ("-create_time",)

    def __str__(self):
        return self.id
