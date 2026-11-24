from django.urls import re_path

from ..views.oj import SampleRunAPI, SubmissionAPI, SubmissionListAPI, SubmissionExistsAPI, SubmissionRankAPI

urlpatterns = [
    re_path(r"^sample_run/?$", SampleRunAPI.as_view(), name="sample_run_api"),
    re_path(r"^submission/?$", SubmissionAPI.as_view(), name="submission_api"),
    re_path(r"^submissions/?$", SubmissionListAPI.as_view(), name="submission_list_api"),
    re_path(r"^submission_exists/?$", SubmissionExistsAPI.as_view(), name="submission_exists"),
    re_path(r"^submission_rank/?$", SubmissionRankAPI.as_view(), name="submission_rank_api"),
]
