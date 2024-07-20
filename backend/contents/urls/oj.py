from django.conf.urls import url

from contents.views.oj import GetHomeStatisticsAPI

urlpatterns = [
    url(r"^home_statistics/?$", GetHomeStatisticsAPI.as_view(), name="home_statistics"),
]