from django import forms
from django.core.validators import RegexValidator
from django.db import models

from school.models import College, Department
from utils.api import serializers, UsernameSerializer

from .models import AdminType, ProblemPermission, User, UserProfile, UserScore, UserSolved


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    tfa_code = serializers.CharField(required=False, allow_blank=True)


class UsernameOrEmailCheckSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=8)
    real_name = serializers.CharField(max_length=13)
    email = serializers.EmailField(max_length=64)
    password = serializers.RegexField(regex=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
                                      min_length=8,
                                      error_messages={'invalid': '비밀번호는 8글자 이상이어야 하며, 영문, 숫자, 특수문자를 모두 포함해야 합니다.'})
    student_id = serializers.RegexField(regex=r'^\d{6,9}$',
                                        min_length=6,
                                        max_length=9,
                                        error_messages={'invalid': '학번은 6자리 이상 9자리 이하의 숫자만 입력 가능합니다.'})
    collegeId = serializers.IntegerField()
    departmentId = serializers.IntegerField()


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.RegexField(regex=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
                                          min_length=8,
                                          error_messages={'invalid': '비밀번호는 8글자 이상이어야 하며, 영문, 숫자, 특수문자를 모두 포함해야 합니다.'})


class GenerateUserSerializer(serializers.Serializer):
    college = serializers.IntegerField()
    department = serializers.IntegerField()
    prefix = serializers.CharField(max_length=10)
    num_of_mock = serializers.IntegerField(min_value=1, max_value=20)


class ImportUserSeralizer(serializers.Serializer):
    users = serializers.ListField(child=serializers.ListField(child=serializers.CharField(max_length=64)))


class DateRangeSerializer(serializers.Serializer):
    start = serializers.DateField()
    end = serializers.DateField()


class WeeklyStatisticsSerializer(serializers.Serializer):
    week_info = serializers.CharField()
    date_range = DateRangeSerializer()
    xAxis = serializers.ListField(child=serializers.CharField())
    series = serializers.ListField(child=serializers.IntegerField())


class MonthlyStatisticsSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    xAxis = serializers.ListField(child=serializers.CharField())
    series = serializers.ListField(child=serializers.IntegerField())


class DepartmentStatSerializer(serializers.Serializer):
    value = serializers.IntegerField()
    name = serializers.CharField()


class UserAdminStatisticsSerializer(serializers.Serializer):
    all_users = serializers.IntegerField()
    super_admins = serializers.IntegerField()
    admins = serializers.IntegerField()
    regular_users = serializers.IntegerField()
    disabled_users = serializers.IntegerField()
    department_statistics = DepartmentStatSerializer(many=True)
    monthly_statistics = MonthlyStatisticsSerializer()
    weekly_statistics = WeeklyStatisticsSerializer()


class UserAdminSerializer(serializers.ModelSerializer):
    real_name = serializers.SerializerMethodField()
    college = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "admin_type", "problem_permission", "real_name", "college", "department",
            "create_time", "last_login", "two_factor_auth", "open_api", "is_disabled", "avatar", "student_id"
        ]

    def get_real_name(self, obj):
        return obj.userprofile.real_name

    def get_college(self, obj):
        return obj.userprofile.school

    def get_department(self, obj):
        return obj.userprofile.major

    def get_avatar(self, obj):
        return obj.userprofile.avatar

    def get_student_id(self, obj):
        return obj.userprofile.student_id


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "admin_type", "problem_permission", "create_time", "last_login",
            "two_factor_auth", "open_api", "is_disabled"
        ]


class EditUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(min_length=3, max_length=8)
    real_name = serializers.CharField(max_length=13)
    password = serializers.RegexField(allow_null=True,
                                      allow_blank=True,
                                      regex=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
                                      min_length=8,
                                      error_messages={'invalid': '비밀번호는 8글자 이상이어야 하며, 영문, 숫자, 특수문자를 모두 포함해야 합니다.'})
    # email = serializers.EmailField(max_length=64)
    admin_type = serializers.ChoiceField(choices=(AdminType.REGULAR_USER, AdminType.ADMIN, AdminType.SUPER_ADMIN))
    problem_permission = serializers.ChoiceField(choices=(ProblemPermission.NONE, ProblemPermission.OWN,
                                                          ProblemPermission.ALL))
    college = serializers.IntegerField(allow_null=True)
    department = serializers.IntegerField(allow_null=True)
    student_id = serializers.CharField(max_length=9,
                                       allow_null=True,
                                       allow_blank=True,
                                       validators=[
                                           RegexValidator(regex=r'^\d{6,9}$',
                                                          message='학번은 6자리 이상 9자리 이하의 숫자만 입력 가능합니다.',
                                                          code='invalid_student_id'),
                                       ])
    open_api = serializers.BooleanField()
    two_factor_auth = serializers.BooleanField()
    is_disabled = serializers.BooleanField()


class ApplyResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    captcha = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.RegexField(regex=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
                                      min_length=8)
    captcha = serializers.CharField()


class SSOSerializer(serializers.Serializer):
    token = serializers.CharField()


class TwoFactorAuthCodeSerializer(serializers.Serializer):
    code = serializers.IntegerField()


class FileUploadForm(forms.Form):
    file = forms.FileField()


class RankInfoSerializer(serializers.ModelSerializer):
    user = UsernameSerializer()

    class Meta:
        model = UserProfile
        fields = "__all__"
