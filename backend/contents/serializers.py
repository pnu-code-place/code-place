from utils.api import serializers
class HomeStatistics(serializers.Serializer):
    total_problem_length = serializers.IntegerField()
    accepted_problem_length = serializers.IntegerField()
    ended_contest_length = serializers.IntegerField()

