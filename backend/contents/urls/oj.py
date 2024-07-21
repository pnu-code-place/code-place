from django.conf.urls import url

from contents.views.oj import GetHomeStatisticsAPI, GetHomeRSSNoticeAPI

urlpatterns = [
    url(r"^home_statistics/?$", GetHomeStatisticsAPI.as_view(), name="home_statistics"),
    url(r"^sw_center_notice/?$", GetHomeRSSNoticeAPI.as_view(), name="home_rss_notice"),
]