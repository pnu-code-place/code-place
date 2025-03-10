from account.models import UserScore, User, Department
from utils.api import serializers


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
