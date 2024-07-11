from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models, transaction
from django.db.models import JSONField

from utils.constants import Tier


class AdminType(object):
    REGULAR_USER = "Regular User"
    ADMIN = "Admin"
    SUPER_ADMIN = "Super Admin"

class ProblemPermission(object):
    NONE = "None"
    OWN = "Own"
    ALL = "All"

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


def get_default_tier():
    return next(iter(Tier.tiers.keys()))


def get_default_current_tier_score():
    return 0


def get_default_next_tier_score():
    return Tier.tiers['bronze3']


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

