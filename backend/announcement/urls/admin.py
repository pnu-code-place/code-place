from django.urls import re_path

from ..views.admin import AnnouncementAdminAPI

urlpatterns = [
    re_path(r"^announcement/?$", AnnouncementAdminAPI.as_view(), name="announcement_admin_api"),
]
