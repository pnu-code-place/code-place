from django.conf.urls import url

from ..views.oj import SubmissionAPI, SubmissionListAPI, SubmissionExistsAPI, SubmissionRankAPI

urlpatterns = [
    url(r"^submission/?$", SubmissionAPI.as_view(), name="submission_api"),
    url(r"^submissions/?$", SubmissionListAPI.as_view(), name="submission_list_api"),
    url(r"^submission_exists/?$", SubmissionExistsAPI.as_view(), name="submission_exists"),
    url(r"^submission_rank/?$", SubmissionRankAPI.as_view(), name="submission_rank_api"),
]
