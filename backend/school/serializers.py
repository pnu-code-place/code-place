from utils.api import serializers


class CollegeListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    college_name = serializers.CharField()


class DepartmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    department_name = serializers.CharField()
    college_id = serializers.IntegerField()
