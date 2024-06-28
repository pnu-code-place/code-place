from django.conf.urls import url

from ..views.oj import (ApplyResetPasswordAPI, ResetPasswordAPI, GetRankingAPI,
                        UserChangePasswordAPI, UserRegisterAPI, UserChangeEmailAPI,
                        UserLoginAPI, UserLogoutAPI, UsernameOrEmailCheck,
                        AvatarUploadAPI, TwoFactorAuthAPI, UserProfileAPI,
                        UserProfileDashBoardAPI,
                        UserRankAPI, CheckTFARequiredAPI, SessionManagementAPI,
                        ProfileProblemDisplayIDRefreshAPI, OpenAPIAppkeyAPI, SSOAPI,
                        ApplyUserEmailValidCheckAPI, UserEmailValidCheckAPI,
                        GetCollegeListAPI, GetDepartmentListAPI, HomeRankingAPI, SurgeUserRankAPI, MajorRankAPI,
                        GetHomeStatisticsAPI)

from utils.captcha.views import CaptchaAPIView

urlpatterns = [
    url(r"^college_list/?$", GetCollegeListAPI.as_view(), name="college_list"),
    url(r"^department_list/?$", GetDepartmentListAPI.as_view(), name="department_list"),
    url(r"^home_statistics/?$", GetHomeStatisticsAPI.as_view(), name="home_statistics"),
    url(r"^ranking/?$", GetRankingAPI.as_view(), name="ranking"),
    url(r"^home_ranking/?$", HomeRankingAPI.as_view(), name="home_ranking"),
    url(r"^login/?$", UserLoginAPI.as_view(), name="user_login_api"),
    url(r"^logout/?$", UserLogoutAPI.as_view(), name="user_logout_api"),
    url(r"^apply_user_email_valid_check/?$", ApplyUserEmailValidCheckAPI.as_view(),
        name="apply_user_email_valid_check"),
    url(r"^user_email_valid_check/?$", UserEmailValidCheckAPI.as_view(), name="user_email_valid_check"),
    url(r"^register/?$", UserRegisterAPI.as_view(), name="user_register_api"),
    url(r"^change_password/?$", UserChangePasswordAPI.as_view(), name="user_change_password_api"),
    url(r"^change_email/?$", UserChangeEmailAPI.as_view(), name="user_change_email_api"),
    url(r"^apply_reset_password/?$", ApplyResetPasswordAPI.as_view(), name="apply_reset_password_api"),
    url(r"^reset_password/?$", ResetPasswordAPI.as_view(), name="reset_password_api"),
    url(r"^captcha/?$", CaptchaAPIView.as_view(), name="show_captcha"),
    url(r"^check_username_or_email", UsernameOrEmailCheck.as_view(), name="check_username_or_email"),
    url(r"^profile/?$", UserProfileAPI.as_view(), name="user_profile_api"),
    url(r"^profile/dashboard/?$", UserProfileDashBoardAPI.as_view(), name="user_profile_dashboard_api"),
    url(r"^profile/fresh_display_id", ProfileProblemDisplayIDRefreshAPI.as_view(), name="display_id_fresh"),
    url(r"^upload_avatar/?$", AvatarUploadAPI.as_view(), name="avatar_upload_api"),
    url(r"^tfa_required/?$", CheckTFARequiredAPI.as_view(), name="tfa_required_check"),
    url(r"^two_factor_auth/?$", TwoFactorAuthAPI.as_view(), name="two_factor_auth_api"),
    url(r"^user_rank/?$", UserRankAPI.as_view(), name="user_rank_api"),
    url(r"^surge_user_rank/?$", SurgeUserRankAPI.as_view(), name="surge_user_rank_api"),
    url(r"^major_rank/?$", MajorRankAPI.as_view(), name="major_rank_api"),
    url(r"^sessions/?$", SessionManagementAPI.as_view(), name="session_management_api"),
    url(r"^open_api_appkey/?$", OpenAPIAppkeyAPI.as_view(), name="open_api_appkey_api"),
    url(r"^sso?$", SSOAPI.as_view(), name="sso_api")
]
