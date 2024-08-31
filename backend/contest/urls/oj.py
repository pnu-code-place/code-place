from django.conf.urls import url

from ..views.oj import ContestAnnouncementListAPI, ContestHistoryListAPI, ContestUnderWayListAPI, \
    ContestNotStartedListAPI
from ..views.oj import ContestPasswordVerifyAPI, ContestAccessAPI
from ..views.oj import ContestListAPI, ContestAPI

urlpatterns = [
    url(r"^contests/?$", ContestListAPI.as_view(), name="contest_list_api"),
    url(r"^contest_history/?$", ContestHistoryListAPI.as_view(), name="contest_history_list_api"),
    url(r"^contest_underway/?$", ContestUnderWayListAPI.as_view(), name="contest_underway_list_api"),
    url(r"^contest_not_started/?$", ContestNotStartedListAPI.as_view(), name="contest_not_started_list_api"),
    url(r"^contest/?$", ContestAPI.as_view(), name="contest_api"),
    url(r"^contest/password/?$", ContestPasswordVerifyAPI.as_view(), name="contest_password_api"),
    url(r"^contest/announcement/?$", ContestAnnouncementListAPI.as_view(), name="contest_announcement_api"),
    url(r"^contest/access/?$", ContestAccessAPI.as_view(), name="contest_access_api"),
]
