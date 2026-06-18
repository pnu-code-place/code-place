from django.urls import re_path

from contents.views.oj import GetHomeStatisticsAPI, GetHomeRSSNoticeAPI, GetHomeAnnouncementAPI

urlpatterns = [
    re_path(r"^home_statistics/?$", GetHomeStatisticsAPI.as_view(), name="home_statistics"),
    re_path(r"^home_announcements/?$", GetHomeAnnouncementAPI.as_view(), name="home_announcements"),
    re_path(r"^sw_center_notice/?$", GetHomeRSSNoticeAPI.as_view(), name="home_rss_notice"),
]