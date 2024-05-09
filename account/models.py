from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings
from django.db import models, transaction
from utils.models import JSONField
from utils.constants import Tier


class AdminType(object):
    REGULAR_USER = "Regular User"
    ADMIN = "Admin"
    SUPER_ADMIN = "Super Admin"


class ProblemPermission(object):
    NONE = "None"
    OWN = "Own"
    ALL = "All"


class College(models.Model):
    college_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'college'


class Department(models.Model):
    college = models.ForeignKey(College, null=True, on_delete=models.SET_NULL)
    department_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'department'


class UserManager(models.Manager):
    use_in_migrations = True

    def get_by_natural_key(self, email):
        return self.get(**{f"{self.model.EMAIL_FIELD}__iexact": email})


class User(AbstractBaseUser):
    username = models.TextField(unique=True)
    email = models.TextField(null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    # One of UserType
    admin_type = models.TextField(default=AdminType.REGULAR_USER)
    problem_permission = models.TextField(default=ProblemPermission.NONE)
    reset_password_token = models.TextField(null=True)
    reset_password_token_expire_time = models.DateTimeField(null=True)
    # SSO auth token
    auth_token = models.TextField(null=True)
    two_factor_auth = models.BooleanField(default=False)
    tfa_token = models.TextField(null=True)
    session_keys = JSONField(default=list)
    # open api key
    open_api = models.BooleanField(default=False)
    open_api_appkey = models.TextField(null=True)
    is_disabled = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def is_admin(self):
        return self.admin_type == AdminType.ADMIN

    def is_super_admin(self):
        return self.admin_type == AdminType.SUPER_ADMIN

    def is_admin_role(self):
        return self.admin_type in [AdminType.ADMIN, AdminType.SUPER_ADMIN]

    def can_mgmt_all_problem(self):
        return self.problem_permission == ProblemPermission.ALL

    def is_contest_admin(self, contest):
        return self.is_authenticated and (contest.created_by == self or self.admin_type == AdminType.SUPER_ADMIN)

    class Meta:
        db_table = "user"


def get_default_field_score():
    return {
        "0": 0,     # "Math"
        "1": 0,     # "Implementation"
        "2": 0,     # "Datastructure"
        "3": 0,     # "Search"
        "4": 0,     # "Sorting"
    }


def get_default_tier():
    return next(iter(Tier.tiers.keys()))


def get_default_current_tier_score():
    return 0


def get_default_next_tier_score():
    return Tier.tiers['bronze3']


def get_default_category_difficulty_score():
    return {'solved': 0, 'score': 0}


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, null=True, on_delete=models.SET_NULL)
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL)
    # acm_problems_status examples:
    # {
    #     "problems": {
    #         "1": {
    #             "status": JudgeStatus.ACCEPTED,
    #             "_id": "1000"
    #         }
    #     },
    #     "contest_problems": {
    #         "1": {
    #             "status": JudgeStatus.ACCEPTED,
    #             "_id": "1000"
    #         }
    #     }
    # }
    acm_problems_status = JSONField(default=dict)
    # like acm_problems_status, merely add "score" field
    oi_problems_status = JSONField(default=dict)

    real_name = models.TextField(null=True)
    student_id = models.TextField(null=True)
    avatar = models.TextField(default=f"{settings.AVATAR_URI_PREFIX}/default.png")
    blog = models.URLField(null=True)
    mood = models.TextField(null=True)
    github = models.TextField(null=True)
    school = models.TextField(null=True)
    major = models.TextField(null=True)
    language = models.TextField(null=True)
    # for ACM
    accepted_number = models.IntegerField(default=0)
    # for OI
    total_score = models.BigIntegerField(default=0)
    submission_number = models.IntegerField(default=0)

    def add_accepted_problem_number(self):
        self.accepted_number = models.F("accepted_number") + 1
        self.save()

    def add_submission_number(self):
        self.submission_number = models.F("submission_number") + 1
        self.save()

    # 计算总分时， 应先减掉上次该题所得分数， 然后再加上本次所得分数
    def add_score(self, this_time_score, last_time_score=None):
        last_time_score = last_time_score or 0
        self.total_score = models.F("total_score") - last_time_score + this_time_score
        self.save()

    class Meta:
        db_table = "user_profile"


class UserScore(models.Model):
    user = models.OneToOneField(User, primary_key=True, unique=True, on_delete=models.CASCADE)

    yesterday_score = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    fluctuation = models.IntegerField(default=0)

    math_score = models.BigIntegerField(default=0)
    implementation_score = models.BigIntegerField(default=0)
    datastructure_score = models.BigIntegerField(default=0)
    search_score = models.BigIntegerField(default=0)
    sorting_score = models.BigIntegerField(default=0)

    VeryLow_score = models.BigIntegerField(default=0)
    Low_score = models.BigIntegerField(default=0)
    Mid_score = models.BigIntegerField(default=0)
    High_score = models.BigIntegerField(default=0)
    VeryHigh_score = models.BigIntegerField(default=0)

    tier = models.TextField(default=get_default_tier)
    current_tier_score = models.IntegerField(default=get_default_current_tier_score)
    next_tier_score = models.IntegerField(default=get_default_next_tier_score)

    @classmethod
    def calculate_basis(cls):
        with transaction.atomic():
            scores = cls.objects.select_for_update().all()
            for user_score in scores:
                user_score.yesterday_score = user_score.total_score
                user_score.fluctuation = 0
                user_score.save()

    @classmethod
    def calculate_fluctuation(cls):
        with transaction.atomic():
            scores = cls.objects.select_for_update().all()
            for user_score in scores:
                user_score.fluctuation = user_score.total_score - user_score.yesterday_score
                user_score.save()

    class Meta:
        db_table = "user_score"


class UserSolved(models.Model):
    user = models.OneToOneField(User, primary_key=True, unique=True, on_delete=models.CASCADE)

    math_solved = models.BigIntegerField(default=0)
    implementation_solved = models.BigIntegerField(default=0)
    datastructure_solved = models.BigIntegerField(default=0)
    search_solved = models.BigIntegerField(default=0)
    sorting_solved = models.BigIntegerField(default=0)

    VeryLow_solved = models.BigIntegerField(default=0)
    Low_solved = models.BigIntegerField(default=0)
    Mid_solved = models.BigIntegerField(default=0)
    High_solved = models.BigIntegerField(default=0)
    VeryHigh_solved = models.BigIntegerField(default=0)

    max_miracle = models.IntegerField(default=0)

    class Meta:
        db_table = "user_solved"

    @property
    def total_solved(self):
        return self.math_solved + self.implementation_solved + self.datastructure_solved + self.search_solved + self.sorting_solved
