from django.conf.urls import url

from ..views.oj import AnnouncementAPI, SWAnnouncementAPI

urlpatterns = [
    url(r"^announcement/?$", AnnouncementAPI.as_view(), name="announcement_api"),
    url(r"^sw_center_notice/?$", SWAnnouncementAPI.as_view(), name="sw_center_notice_api"),
]
