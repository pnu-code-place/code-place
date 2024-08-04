from django.conf.urls import url

from account.views.oj import ProfileProblemDisplayIDRefreshAPI
from profile.views.oj import ProfileProblemAPIView, UserProfileAPI, UserProfileDashBoardAPI, AvatarUploadAPI

urlpatterns = [
    url(r"^profile/?$", UserProfileAPI.as_view(), name="user_profile_api"),
    url(r"^profile/dashboard/?$", UserProfileDashBoardAPI.as_view(), name="user_profile_dashboard_api"),
    url(r"^profile/fresh_display_id", ProfileProblemDisplayIDRefreshAPI.as_view(), name="display_id_fresh"),
    url(r"^profile/problem/?$", ProfileProblemAPIView.as_view(), name="profile_problem_api"),
    url(r"^upload_avatar/?$", AvatarUploadAPI.as_view(), name="avatar_upload_api"),
]