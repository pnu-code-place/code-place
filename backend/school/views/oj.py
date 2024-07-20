from school.models import College, Department
from school.serializers import CollegeListSerializer, DepartmentSerializer
from utils.api import APIView


class GetCollegeListAPI(APIView):
    def get(self, request):
        try:
            college_list = College.objects.all()
        except College.DoesNotExist:
            return self.error("failed to get college list")
        return self.success(CollegeListSerializer(college_list, many=True).data)

class GetDepartmentListAPI(APIView):

    def get(self, request):
        try:
            college_id = request.GET.get("college_id")
            department_list = Department.objects.filter(college=college_id).order_by('id')
        except Department.DoesNotExist:
            return self.error("failed to get department list")
        return self.success(DepartmentSerializer(department_list, many=True).data)