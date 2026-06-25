from .models import JudgeStatus, Submission
from utils.api import serializers
from utils.serializers import LanguageNameChoiceField


class CreateSubmissionSerializer(serializers.Serializer):
    problem_id = serializers.IntegerField()
    language = LanguageNameChoiceField()
    code = serializers.CharField(max_length=1024 * 1024)
    contest_id = serializers.IntegerField(required=False)
    captcha = serializers.CharField(required=False)


class ShareSubmissionSerializer(serializers.Serializer):
    id = serializers.CharField()
    shared = serializers.BooleanField()


class SubmissionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Submission
        fields = "__all__"


# 不显示submission info的serializer, 用于ACM rule_type
class SubmissionSafeModelSerializer(serializers.ModelSerializer):
    problem = serializers.SlugRelatedField(read_only=True, slug_field="_id")

    class Meta:
        model = Submission
        exclude = ("info", "contest", "ip")


class SubmissionListSerializer(serializers.ModelSerializer):
    problem = serializers.SlugRelatedField(read_only=True, slug_field="_id")
    problem_id = serializers.SerializerMethodField()
    result_display = serializers.SerializerMethodField()
    show_link = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Submission
        exclude = ("info", "contest", "code", "ip")

    def get_show_link(self, obj):
        # 没传user或为匿名user
        if self.user is None or not self.user.is_authenticated:
            return False
        return obj.check_user_permission(self.user)

    def get_user_avatar(self, obj):
        return obj.user_avatar

    def get_problem_id(self, obj):
        return obj.problem._id

    def get_result_display(self, obj):
        return {
            JudgeStatus.COMPILE_ERROR: "컴파일 에러",
            JudgeStatus.WRONG_ANSWER: "오답",
            JudgeStatus.ACCEPTED: "정답",
            JudgeStatus.CPU_TIME_LIMIT_EXCEEDED: "시간 초과",
            JudgeStatus.REAL_TIME_LIMIT_EXCEEDED: "시간 초과",
            JudgeStatus.MEMORY_LIMIT_EXCEEDED: "메모리 초과",
            JudgeStatus.RUNTIME_ERROR: "런타임 에러",
            JudgeStatus.SYSTEM_ERROR: "시스템 에러",
            JudgeStatus.PENDING: "대기 중",
            JudgeStatus.JUDGING: "채점 중",
            JudgeStatus.PARTIALLY_ACCEPTED: "부분 정답",
        }.get(obj.result, obj.result)
