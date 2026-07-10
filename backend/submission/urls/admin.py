from django.urls import re_path

from ..views.admin import SubmissionRejudgeAPI
from ..views.oj import ContestSubmissionListAPI

urlpatterns = [
    re_path(r"^submission/rejudge?$", SubmissionRejudgeAPI.as_view(), name="submission_rejudge_api"),
    re_path(r"^contest_submissions/?$", ContestSubmissionListAPI.as_view(), name="contest_submission_list_api"),
]
