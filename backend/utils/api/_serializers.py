from rest_framework import serializers


class UsernameSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    real_name = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()
    school = serializers.SerializerMethodField()
    major = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.need_real_name = kwargs.pop("need_real_name", False)
        super().__init__(*args, **kwargs)

    def get_real_name(self, obj):
        return obj.userprofile.real_name if self.need_real_name else None

    def get_student_id(self, obj):
        return obj.userprofile.student_id

    def get_school(self, obj):
        return obj.userprofile.school

    def get_major(self, obj):
        return obj.userprofile.major