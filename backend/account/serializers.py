from django import forms

from utils.api import serializers, UsernameSerializer

from .models import AdminType, ProblemPermission, User, UserProfile, UserScore, Department, College, UserSolved


class CollegeListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    college_name = serializers.CharField()


class DepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    department_name = serializers.CharField()
    college_id = serializers.IntegerField()

class HomeStatistics(serializers.Serializer):
    total_problem_length = serializers.IntegerField()
    accepted_problem_length = serializers.IntegerField()
    ended_contest_length = serializers.IntegerField()


class RankingSerializer(serializers.ModelSerializer):
    class Meta:
        user = serializers.ReadOnlyField(source="User.id")

        model = UserScore
        fields = ["score", "fluctuation", "user", "basis"]



class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    tfa_code = serializers.CharField(required=False, allow_blank=True)


class UsernameOrEmailCheckSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32)
    real_name = serializers.CharField(max_length=32)
    email = serializers.EmailField(max_length=64)
    password = serializers.CharField(min_length=6)
    student_id = serializers.CharField(min_length=6)
    collegeId = serializers.IntegerField()
    departmentId = serializers.IntegerField()


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)
    tfa_code = serializers.CharField(required=False, allow_blank=True)


class UserChangeEmailSerializer(serializers.Serializer):
    password = serializers.CharField()
    new_email = serializers.EmailField(max_length=64)
    tfa_code = serializers.CharField(required=False, allow_blank=True)


class GenerateUserSerializer(serializers.Serializer):
    prefix = serializers.CharField(max_length=16, allow_blank=True)
    suffix = serializers.CharField(max_length=16, allow_blank=True)
    number_from = serializers.IntegerField()
    number_to = serializers.IntegerField()
    password_length = serializers.IntegerField(max_value=16, default=8)


class ImportUserSeralizer(serializers.Serializer):
    users = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField(max_length=64)))


class UserAdminSerializer(serializers.ModelSerializer):
    real_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "admin_type", "problem_permission", "real_name",
                  "create_time", "last_login", "two_factor_auth", "open_api", "is_disabled"]

    def get_real_name(self, obj):
        return obj.userprofile.real_name


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "admin_type", "problem_permission",
                  "create_time", "last_login", "two_factor_auth", "open_api", "is_disabled"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    real_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.show_real_name = kwargs.pop("show_real_name", False)
        super(UserProfileSerializer, self).__init__(*args, **kwargs)

    def get_real_name(self, obj):
        return obj.real_name if self.show_real_name else None

class UserRankListSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    username = serializers.CharField()  # 수정
    mood = serializers.CharField(source='userprofile.mood')  # 수정
    score = serializers.IntegerField(source='userscore.total_score')  # 수정
    major = serializers.CharField(source='userprofile.major')  # 수정
    tier = serializers.CharField(source='userscore.tier')  # 수정
    solved = serializers.SerializerMethodField()
    growth = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['rank', 'avatar', 'username', 'mood', 'score', 'major', 'tier', 'solved', 'growth']

    def get_rank(self, obj):
        return self.context['rank']

    def get_avatar(self, obj):
        return obj.userprofile.avatar

    def get_growth(self, obj):
        return obj.userscore.fluctuation

    def get_solved(self, obj):  # 추가
        return obj.usersolved.total_solved


class SurgeUserSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    username = serializers.CharField()
    mood = serializers.CharField(source='userprofile.mood')
    score = serializers.IntegerField(source='userscore.total_score')
    major = serializers.CharField(source='userprofile.major')
    tier = serializers.CharField(source='userscore.tier')
    solved = serializers.SerializerMethodField()
    growth = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['rank', 'avatar', 'username', 'mood', 'score', 'major', 'tier', 'solved', 'growth']

    def get_rank(self, obj):
        return self.context['rank']

    def get_avatar(self, obj):
        return obj.userprofile.avatar

    def get_solved(self, obj):
        return obj.usersolved.total_solved

    def get_growth(self, obj):
        return obj.userscore.fluctuation

class MajorRankListSerializer(serializers.ModelSerializer):
    rank = serializers.IntegerField()
    major = serializers.CharField()
    score = serializers.IntegerField()
    people = serializers.IntegerField()

    class Meta:
        model = Department
        fields = ['rank', 'major', 'score', 'people']

class DashboardUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


class DashboardSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['accepted_number', 'submission_number']


class DashboardCollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ['college_name']


class DashboardDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['department_name']


class DashboardRankSerializer(serializers.ModelSerializer):
    total_rank = serializers.SerializerMethodField()
    total_rank_percentage = serializers.SerializerMethodField()

    class Meta:
        model = UserScore
        fields = ['tier', 'total_rank', 'total_rank_percentage', 'total_score', 'current_tier_score', 'next_tier_score' ]

    def get_total_rank(self, instance):
        return instance.total_rank

    def get_total_rank_percentage(self, instance):
        total_rank_percentage = round(instance.total_rank / self.context['total_user_count'], 2)
        return total_rank_percentage

class DashboardFieldInfoSerializer(serializers.ModelSerializer):
    fieldInfo = serializers.SerializerMethodField()

    class Meta:
        model = UserScore
        fields = ['fieldInfo']

    def get_fieldInfo(self, instance):
        field_info = {}
        fields = ['datastructure', 'math', 'sorting', 'implementation', 'search']

        for field in fields:
            field_name_score = f"{field}_score"
            user_field_score = getattr(instance, field_name_score)

            field_rank = UserScore.objects.filter(**{f'{field_name_score}__gt': user_field_score}).count() + 1
            total_users = UserScore.objects.count()
            rank_percentage = (field_rank / total_users)

            field_info[field] = {
                'score': user_field_score,
                'ranking': field_rank,
                'ranking_percent': rank_percentage,
            }

        return field_info

class DashboardDifficultyInfoSerializer(serializers.ModelSerializer):
    difficultyInfo = serializers.SerializerMethodField()

    class Meta:
        model = UserSolved
        fields = ['difficultyInfo']

    def get_difficultyInfo(self, instance):
        difficulty_info = {}
        difficulties = ['VeryLow', 'Low', 'Mid', 'High', 'VeryHigh']

        for difficulty in difficulties:
            solved_field = f"{difficulty}_solved"
            score_field = f"{difficulty}_score"

            solved_count = getattr(instance, solved_field)
            total_score = getattr(UserScore.objects.get(user=instance.user), score_field)

            difficulty_info[difficulty.lower()] = {
                'solve_number': solved_count,
                'total_score': total_score,
            }

        return difficulty_info


class HomeRankingSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = UserScore
        fields = ['avatar', 'tier', 'username', 'total_score', 'fluctuation']

    def get_avatar(self, obj):
        return obj.user.userprofile.avatar

    def get_username(self, obj):
        return obj.user.username


class EditUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=32)
    real_name = serializers.CharField(max_length=32, allow_blank=True, allow_null=True)
    password = serializers.CharField(min_length=6, allow_blank=True, required=False, default=None)
    email = serializers.EmailField(max_length=64)
    admin_type = serializers.ChoiceField(choices=(AdminType.REGULAR_USER, AdminType.ADMIN, AdminType.SUPER_ADMIN))
    problem_permission = serializers.ChoiceField(choices=(ProblemPermission.NONE, ProblemPermission.OWN,
                                                          ProblemPermission.ALL))
    open_api = serializers.BooleanField()
    two_factor_auth = serializers.BooleanField()
    is_disabled = serializers.BooleanField()


class EditUserProfileSerializer(serializers.Serializer):
    real_name = serializers.CharField(max_length=32, allow_null=True, required=False)
    avatar = serializers.CharField(max_length=256, allow_blank=True, required=False)
    blog = serializers.URLField(max_length=256, allow_blank=True, required=False)
    mood = serializers.CharField(max_length=256, allow_blank=True, required=False)
    github = serializers.URLField(max_length=256, allow_blank=True, required=False)
    school = serializers.CharField(max_length=64, allow_blank=True, required=False)
    major = serializers.CharField(max_length=64, allow_blank=True, required=False)
    language = serializers.CharField(max_length=32, allow_blank=True, required=False)


class ApplyResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    captcha = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=6)
    captcha = serializers.CharField()


class SSOSerializer(serializers.Serializer):
    token = serializers.CharField()


class TwoFactorAuthCodeSerializer(serializers.Serializer):
    code = serializers.IntegerField()


class ImageUploadForm(forms.Form):
    image = forms.FileField()


class FileUploadForm(forms.Form):
    file = forms.FileField()


class RankInfoSerializer(serializers.ModelSerializer):
    user = UsernameSerializer()

    class Meta:
        model = UserProfile
        fields = "__all__"
