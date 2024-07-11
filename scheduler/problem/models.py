from django.db import models
from django.db.models import JSONField, Choices

from account.models import User
from contest.models import Contest
from utils.models import RichTextField


class ProblemTag(models.Model):
    name = models.TextField()

    class Meta:
        db_table = "problem_tag"


class ProblemRuleType(Choices):
    ACM = "ACM"
    OI = "OI"


class ProblemDifficulty(object):
    VERYLOW = "VeryLow"
    LOW = "Low"
    MID = "Mid"
    HIGH = "High"
    VERYHIGH = "VeryHigh"


class ProblemIOMode(Choices):
    standard = "Standard IO"
    file = "File IO"


def _default_io_mode():
    return {"io_mode": ProblemIOMode.standard, "input": "input.txt", "output": "output.txt"}


def get_default_week_info():
    return {'submission': 0, 'accepted': 0, 'success_rate': 0.0, 'solver': []}

def get_default_week_info():
    return {'submission': 0, 'accepted': 0, 'success_rate': 0.0, 'solver': []}

class Problem(models.Model):
    # display ID
    _id = models.TextField(db_index=True)
    contest = models.ForeignKey(Contest, null=True, on_delete=models.CASCADE)
    # for contest problem
    is_public = models.BooleanField(default=False)
    title = models.TextField()
    # HTML
    description = RichTextField()
    input_description = RichTextField()
    output_description = RichTextField()
    # [{input: "test", output: "123"}, {input: "test123", output: "456"}]
    samples = JSONField()
    test_case_id = models.TextField()
    # [{"input_name": "1.in", "output_name": "1.out", "score": 0}]
    test_case_score = JSONField()
    hint = RichTextField(null=True)
    languages = JSONField()
    template = JSONField()
    create_time = models.DateTimeField(auto_now_add=True)
    # we can not use auto_now here
    last_update_time = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    solved_by = models.ManyToManyField(User, related_name='problem_solved_by', blank=True)
    # ms
    time_limit = models.IntegerField()
    # MB
    memory_limit = models.IntegerField()
    # io mode
    io_mode = JSONField(default=_default_io_mode)
    # special judge related
    spj = models.BooleanField(default=False)
    spj_language = models.TextField(null=True)
    spj_code = models.TextField(null=True)
    spj_version = models.TextField(null=True)
    spj_compile_ok = models.BooleanField(default=False)
    rule_type = models.TextField()
    visible = models.BooleanField(default=True)
    source = models.TextField(null=True)

    # for distribute Problem
    field = models.IntegerField(default=0)
    difficulty = models.TextField()
    tags = models.ManyToManyField(ProblemTag)

    # for OI mode
    total_score = models.IntegerField(default=0)
    submission_number = models.BigIntegerField(default=0)
    accepted_number = models.BigIntegerField(default=0)

    # {JudgeStatus.ACCEPTED: 3, JudgeStaus.WRONG_ANSWER: 11}, the number means count
    statistic_info = JSONField(default=dict)
    share_submission = models.BooleanField(default=False)

    # 지난 주 정보
    last_week_info = models.JSONField(default=get_default_week_info)

    # 이번 주 정보
    curr_week_info = models.JSONField(default=get_default_week_info)

    is_most_difficult = models.BooleanField(default=False)
    is_bonus = models.BooleanField(default=False)

    class Meta:
        db_table = "problem"
        unique_together = (("_id", "contest"),)
        ordering = ("create_time",)

