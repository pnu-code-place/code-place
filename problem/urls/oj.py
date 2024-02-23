from django.conf.urls import url

from ..views.oj import ProblemTagAPI, ProblemAPI, ContestProblemAPI, PickOneAPI, AIRecommendProblemAPI, BonusProblemAPI

urlpatterns = [
    url(r"^problem/tags/?$", ProblemTagAPI.as_view(), name="problem_tag_list_api"),
    url(r"^problem/?$", ProblemAPI.as_view(), name="problem_api"),
    url(r"^problem/bonus/?$", BonusProblemAPI.as_view(), name="bonus_problem_api"),
    url(r"^pickone/?$", PickOneAPI.as_view(), name="pick_one_api"),
    url(r"^contest/problem/?$", ContestProblemAPI.as_view(), name="contest_problem_api"),
    url(r"^ai_recommend_problem/?$", AIRecommendProblemAPI.as_view(), name="ai_recommend_problem_api"),
]
