from django.urls import re_path

from ..views.admin import ContestAnnouncementAPI, ContestAPI, ACMContestHelper, DownloadContestSubmissions
from ..views.oj import ContestRankAPI, ContestParticipantsAPI

urlpatterns = [
    re_path(r"^contest/?$", ContestAPI.as_view(), name="contest_admin_api"),
    re_path(r"^contest/announcement/?$", ContestAnnouncementAPI.as_view(), name="contest_announcement_admin_api"),
    re_path(r"^contest/acm_helper/?$", ACMContestHelper.as_view(), name="acm_contest_helper"),
    re_path(r"^download_submissions/?$", DownloadContestSubmissions.as_view(), name="acm_contest_helper"),
    re_path(r"^contest_rank/?$", ContestRankAPI.as_view(), name="contest_rank_api"),
    re_path(r"^contest_participants/?$", ContestParticipantsAPI.as_view(), name="contest_participants_api"),
]
