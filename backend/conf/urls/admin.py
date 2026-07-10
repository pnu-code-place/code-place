from django.urls import re_path

from ..views import SMTPAPI, JudgeServerAPI, WebsiteConfigAPI, TestCasePruneAPI, SMTPTestAPI
from ..views import ReleaseNotesAPI, DashboardInfoAPI

urlpatterns = [
    re_path(r"^smtp/?$", SMTPAPI.as_view(), name="smtp_admin_api"),
    re_path(r"^smtp_test/?$", SMTPTestAPI.as_view(), name="smtp_test_api"),
    re_path(r"^website/?$", WebsiteConfigAPI.as_view(), name="website_config_api"),
    re_path(r"^judge_server/?$", JudgeServerAPI.as_view(), name="judge_server_api"),
    re_path(r"^prune_test_case/?$", TestCasePruneAPI.as_view(), name="prune_test_case_api"),
    re_path(r"^versions/?$", ReleaseNotesAPI.as_view(), name="get_release_notes_api"),
    re_path(r"^dashboard_info", DashboardInfoAPI.as_view(), name="dashboard_info_api"),
]
