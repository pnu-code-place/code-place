from django import forms

from account.models import UserScore, UserSolved, UserProfile, User
from account.serializers import UserSerializer
from school.models import College, Department
from utils.api import serializers


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


class EditUserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=8)
    avatar = serializers.CharField(max_length=256, allow_blank=True, required=False)
    mood = serializers.CharField(max_length=256, allow_blank=True, required=False, allow_null=True)
    github = serializers.URLField(max_length=256, allow_blank=True, required=False, allow_null=True)
    college = serializers.IntegerField(allow_null=True, required=False)
    department = serializers.IntegerField(allow_null=True, required=False)
    language = serializers.ChoiceField(allow_null=True, allow_blank=True, required=False, choices=["C", "C++", "Java", "Python3", "JavaScript"])

class ProfileProblemSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    submitTime = serializers.DateTimeField()
    difficulty = serializers.CharField()
    field = serializers.CharField()


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
        fields = ['tier', 'total_rank', 'total_rank_percentage', 'total_score', 'current_tier_score', 'next_tier_score']

    def _get_user_rank(self, instance):
        if not hasattr(self, '_rank_cache'):
            queryset = UserScore.objects.order_by('-total_score')
            user_list = list(queryset)
            self._rank_cache = user_list.index(instance) + 1
        return self._rank_cache

    def get_total_rank(self, instance):
        return self._get_user_rank(instance)

    def get_total_rank_percentage(self, instance):
        rank = self._get_user_rank(instance)
        total_rank_percentage = round(rank / self.context['total_user_count'], 2)
        return total_rank_percentage


class DashboardFieldInfoSerializer(serializers.ModelSerializer):
    fieldInfo = serializers.SerializerMethodField()

    class Meta:
        model = UserScore
        fields = ['fieldInfo']

    def get_fieldInfo(self, instance):
        field_info = {}
        fields = ['datastructure', 'math', 'sorting', 'implementation', 'search', 'algorithm']

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


class ImageUploadForm(forms.Form):
    image = forms.FileField()
