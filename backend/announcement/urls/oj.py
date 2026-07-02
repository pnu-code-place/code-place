from django.urls import re_path

from ..views.oj import AnnouncementAPI

urlpatterns = [
    re_path(r"^announcement/?$", AnnouncementAPI.as_view(), name="announcement_api"),
]
