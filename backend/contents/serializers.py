from announcement.models import Announcement
from utils.api import serializers


class HomeStatistics(serializers.Serializer):
    total_problem_length = serializers.IntegerField()
    accepted_problem_length = serializers.IntegerField()
    ended_contest_length = serializers.IntegerField()


class HomeAnnouncementsSerializer(serializers.Serializer):
    class Meta:
        model = Announcement
        fields = ["id", "title", "create_time"]


class RSSItemSerializer(serializers.Serializer):
    title = serializers.CharField()
    link = serializers.URLField()
    pubDate = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
