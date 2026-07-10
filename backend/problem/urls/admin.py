from django.urls import re_path

from ..views.admin import (ContestProblemAPI, ProblemAPI, TestCaseAPI, MakeContestProblemPublicAPIView, CompileSPJAPI,
                           AddContestProblemAPI, ExportProblemAPI, ImportProblemAPI, FPSProblemImport,
                           ProblemIdDuplicateCheckAPI, ImportContestProblemAPI)

urlpatterns = [
    re_path(r"^test_case/?$", TestCaseAPI.as_view(), name="test_case_api"),
    re_path(r"^compile_spj/?$", CompileSPJAPI.as_view(), name="compile_spj"),
    re_path(r"^problem/?$", ProblemAPI.as_view(), name="problem_admin_api"),
    re_path(r"^problem/check_duplicate_id?$",
        ProblemIdDuplicateCheckAPI.as_view(),
        name="problem_admin_duplicate_check_api"),
    re_path(r"^contest/problem/?$", ContestProblemAPI.as_view(), name="contest_problem_admin_api"),
    re_path(r"^contest_problem/make_public/?$", MakeContestProblemPublicAPIView.as_view(), name="make_public_api"),
    re_path(r"^contest/add_problem_from_public/?$",
        AddContestProblemAPI.as_view(),
        name="add_contest_problem_from_public_api"),
    re_path(r"^contest/import_problem/?$", ImportContestProblemAPI.as_view(), name="import_contest_problem_api"),
    re_path(r"^export_problem/?$", ExportProblemAPI.as_view(), name="export_problem_api"),
    re_path(r"^import_problem/?$", ImportProblemAPI.as_view(), name="import_problem_api"),
    re_path(r"^import_fps/?$", FPSProblemImport.as_view(), name="fps_problem_api"),
]
