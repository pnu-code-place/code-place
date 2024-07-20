from django.conf.urls import url

from ranking.views.oj import HomeRankingAPI, UserRankAPI, SurgeUserRankAPI, MajorRankAPI

urlpatterns = [
    url(r"^home_ranking/?$", HomeRankingAPI.as_view(), name="home_ranking"),
    url(r"^user_rank/?$", UserRankAPI.as_view(), name="user_rank_api"),
    url(r"^surge_user_rank/?$", SurgeUserRankAPI.as_view(), name="surge_user_rank_api"),
    url(r"^major_rank/?$", MajorRankAPI.as_view(), name="major_rank_api"),
]