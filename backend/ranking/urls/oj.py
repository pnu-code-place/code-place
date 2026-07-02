from django.urls import re_path

from ranking.views.oj import HomeRankingAPI, UserRankAPI, SurgeUserRankAPI, MajorRankAPI

urlpatterns = [
    re_path(r"^home_ranking/?$", HomeRankingAPI.as_view(), name="home_ranking_api"),
    re_path(r"^user_rank/?$", UserRankAPI.as_view(), name="user_rank_api"),
    re_path(r"^surge_user_rank/?$", SurgeUserRankAPI.as_view(), name="surge_user_rank_api"),
    re_path(r"^major_rank/?$", MajorRankAPI.as_view(), name="major_rank_api"),
]