from django.conf.urls import url

from school.views.oj import GetCollegeListAPI, GetDepartmentListAPI

urlpatterns = [
    url(r"^college_list/?$", GetCollegeListAPI.as_view(), name="college_list"),
    url(r"^department_list/?$", GetDepartmentListAPI.as_view(), name="department_list"),
]