from django.urls import re_path

from ..views.admin import UserAdminAPI, GenerateUserAPI, UserAdminStatisticAPI

urlpatterns = [
    re_path(r"^user/?$", UserAdminAPI.as_view(), name="user_admin_api"),
    re_path(r"^stat/?$", UserAdminStatisticAPI.as_view(), name="user_admin_stat_api"),
    re_path(r"^generate_user/?$", GenerateUserAPI.as_view(), name="generate_user_api"),
]
