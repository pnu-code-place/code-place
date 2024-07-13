from utils.api import serializers


class ProfileProblemSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    submitTime = serializers.DateTimeField()
    difficulty = serializers.CharField()
    field = serializers.CharField()
