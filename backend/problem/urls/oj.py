from django.conf.urls import url

from ..views.oj import (BonusProblemAPI, ContestProblemAPI, MostDifficultProblemAPI, PickOneAPI, ProblemAPI,
                        ProblemLLMHintAPI, ProblemTagAPI, RecommendProblemAPI, UpdateBonusProblemAPI,
                        UpdateWeeklyStatsAPI, AIHintHistoryAPI)

urlpatterns = [
    url(r"^problem/tags/?$", ProblemTagAPI.as_view(), name="problem_tag_list_api"),
    url(r"^problem/?$", ProblemAPI.as_view(), name="problem_api"),
    url(r"^problem/llm_hint/?$", ProblemLLMHintAPI.as_view(), name="problem_llm_hint_api"),
    url(r"^problem/ai_hint_history/?$", AIHintHistoryAPI.as_view(), name="problem_ai_hint_history_api"),
    url(r"^problem/bonus/?$", BonusProblemAPI.as_view(), name="bonus_problem_api"),
    url(r"^pickone/?$", PickOneAPI.as_view(), name="pick_one_api"),
    url(r"^contest/problem/?$", ContestProblemAPI.as_view(), name="contest_problem_api"),
    url(r"^recommend_problem/?$", RecommendProblemAPI.as_view(), name="recommend_problem_api"),
    url(r"^problem/most_difficult_problem/?$", MostDifficultProblemAPI.as_view(), name="most_difficult_problem_api"),
    url(r"^problem/update_weekly_stats/?$", UpdateWeeklyStatsAPI.as_view(), name="update_weekly_stats_api"),
    url(r"^problem/update_bonus_problem/?$", UpdateBonusProblemAPI.as_view(), name="update_bonus_problem_api"),
]
