from django.urls import re_path

from ..views.oj import SubmissionAPI, SubmissionListAPI, SubmissionExistsAPI, SubmissionRankAPI

urlpatterns = [
    re_path(r"^submission/?$", SubmissionAPI.as_view(), name="submission_api"),
    re_path(r"^submissions/?$", SubmissionListAPI.as_view(), name="submission_list_api"),
    re_path(r"^submission_exists/?$", SubmissionExistsAPI.as_view(), name="submission_exists"),
    re_path(r"^submission_rank/?$", SubmissionRankAPI.as_view(), name="submission_rank_api"),
]
