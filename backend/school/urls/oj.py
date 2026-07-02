from django.urls import re_path

from school.views.oj import GetCollegeListAPI, GetDepartmentListAPI

urlpatterns = [
    re_path(r"^college_list/?$", GetCollegeListAPI.as_view(), name="college_list"),
    re_path(r"^department_list/?$", GetDepartmentListAPI.as_view(), name="department_list"),
]