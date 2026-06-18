from django.urls import re_path

from account.views.oj import ProfileProblemDisplayIDRefreshAPI
from profile.views.oj import ProfileProblemAPIView, UserProfileAPI, UserProfileDashBoardAPI, AvatarUploadAPI

urlpatterns = [
    re_path(r"^profile/?$", UserProfileAPI.as_view(), name="user_profile_api"),
    re_path(r"^profile/dashboard/?$", UserProfileDashBoardAPI.as_view(), name="user_profile_dashboard_api"),
    re_path(r"^profile/fresh_display_id", ProfileProblemDisplayIDRefreshAPI.as_view(), name="display_id_fresh"),
    re_path(r"^profile/problem/?$", ProfileProblemAPIView.as_view(), name="profile_problem_api"),
    re_path(r"^upload_avatar/?$", AvatarUploadAPI.as_view(), name="avatar_upload_api"),
]