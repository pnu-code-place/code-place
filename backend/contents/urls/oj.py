from django.conf.urls import url

urlpatterns = [
    url(r"^home_statistics/?$", GetHomeStatisticsAPI.as_view(), name="home_statistics"),
]