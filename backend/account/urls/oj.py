from django.urls import re_path

from ..views.oj import (ApplyResetPasswordAPI, CalculateUserScoreBasisAPI, CalculateUserScoreFluctuationAPI,
                        ResetPasswordAPI, UserChangePasswordAPI, UserRegisterAPI, UserLoginAPI, UserLogoutAPI,
                        UsernameOrEmailCheck, TwoFactorAuthAPI, CheckTFARequiredAPI, SessionManagementAPI,
                        OpenAPIAppkeyAPI, SSOAPI, ApplyUserEmailValidCheckAPI, UserEmailValidCheckAPI,
                        NicknameValidCheckAPI)

from utils.captcha.views import CaptchaAPIView

urlpatterns = [
    re_path(r"^login/?$", UserLoginAPI.as_view(), name="user_login_api"),
    re_path(r"^logout/?$", UserLogoutAPI.as_view(), name="user_logout_api"),
    re_path(r"^apply_user_email_valid_check/?$", ApplyUserEmailValidCheckAPI.as_view(),
        name="apply_user_email_valid_check"),
    re_path(r"^user_email_valid_check/?$", UserEmailValidCheckAPI.as_view(), name="user_email_valid_check"),
    re_path(r"^nickname_valid_check/?$", NicknameValidCheckAPI.as_view(), name="user_nickname_valid_check"),
    re_path(r"^register/?$", UserRegisterAPI.as_view(), name="user_register_api"),
    re_path(r"^change_password/?$", UserChangePasswordAPI.as_view(), name="user_change_password_api"),
    re_path(r"^apply_reset_password/?$", ApplyResetPasswordAPI.as_view(), name="apply_reset_password_api"),
    re_path(r"^reset_password/?$", ResetPasswordAPI.as_view(), name="reset_password_api"),
    re_path(r"^captcha/?$", CaptchaAPIView.as_view(), name="show_captcha"),
    re_path(r"^check_username_or_email", UsernameOrEmailCheck.as_view(), name="check_username_or_email"),
    re_path(r"^tfa_required/?$", CheckTFARequiredAPI.as_view(), name="tfa_required_check"),
    re_path(r"^two_factor_auth/?$", TwoFactorAuthAPI.as_view(), name="two_factor_auth_api"),
    re_path(r"^sessions/?$", SessionManagementAPI.as_view(), name="session_management_api"),
    re_path(r"^open_api_appkey/?$", OpenAPIAppkeyAPI.as_view(), name="open_api_appkey_api"),
    re_path(r"^sso?$", SSOAPI.as_view(), name="sso_api"),
    re_path(r"^calc_user_score_basis/?$", CalculateUserScoreBasisAPI.as_view(), name="calculate_user_score_basis_api"),
    re_path(r"^calc_user_score_fluctuation/?$",
        CalculateUserScoreFluctuationAPI.as_view(),
        name="calculate_user_score_fluctuation_api")
]
