from django.conf.urls import url

from ..views.admin import SubmissionRejudgeAPI
from ..views.oj import ContestSubmissionListAPI

urlpatterns = [
    url(r"^submission/rejudge?$", SubmissionRejudgeAPI.as_view(), name="submission_rejudge_api"),
    url(r"^contest_submissions/?$", ContestSubmissionListAPI.as_view(), name="contest_submission_list_api"),
]
