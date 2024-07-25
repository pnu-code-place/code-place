from django.conf.urls import url

from ..views.admin import UserAdminAPI, GenerateUserAPI, UserAdminStatisticAPI

urlpatterns = [
    url(r"^user/?$", UserAdminAPI.as_view(), name="user_admin_api"),
    url(r"^stat/?$", UserAdminStatisticAPI.as_view(), name="user_admin_stat_api"),
    url(r"^generate_user/?$", GenerateUserAPI.as_view(), name="generate_user_api"),
]
