from django.conf.urls import url

from ..views.oj import (ApplyResetPasswordAPI, ResetPasswordAPI,
                        UserChangePasswordAPI, UserRegisterAPI,
                        UserLoginAPI, UserLogoutAPI, UsernameOrEmailCheck,
                        TwoFactorAuthAPI, CheckTFARequiredAPI, SessionManagementAPI,
                        OpenAPIAppkeyAPI, SSOAPI, ApplyUserEmailValidCheckAPI,
                        UserEmailValidCheckAPI, NicknameValidCheckAPI)

from utils.captcha.views import CaptchaAPIView

urlpatterns = [
    url(r"^login/?$", UserLoginAPI.as_view(), name="user_login_api"),
    url(r"^logout/?$", UserLogoutAPI.as_view(), name="user_logout_api"),
    url(r"^apply_user_email_valid_check/?$", ApplyUserEmailValidCheckAPI.as_view(),
        name="apply_user_email_valid_check"),
    url(r"^user_email_valid_check/?$", UserEmailValidCheckAPI.as_view(), name="user_email_valid_check"),
    url(r"^nickname_valid_check/?$", NicknameValidCheckAPI.as_view(), name="user_nickname_valid_check"),
    url(r"^register/?$", UserRegisterAPI.as_view(), name="user_register_api"),
    url(r"^change_password/?$", UserChangePasswordAPI.as_view(), name="user_change_password_api"),
    url(r"^apply_reset_password/?$", ApplyResetPasswordAPI.as_view(), name="apply_reset_password_api"),
    url(r"^reset_password/?$", ResetPasswordAPI.as_view(), name="reset_password_api"),
    url(r"^captcha/?$", CaptchaAPIView.as_view(), name="show_captcha"),
    url(r"^check_username_or_email", UsernameOrEmailCheck.as_view(), name="check_username_or_email"),
    url(r"^tfa_required/?$", CheckTFARequiredAPI.as_view(), name="tfa_required_check"),
    url(r"^two_factor_auth/?$", TwoFactorAuthAPI.as_view(), name="two_factor_auth_api"),
    url(r"^sessions/?$", SessionManagementAPI.as_view(), name="session_management_api"),
    url(r"^open_api_appkey/?$", OpenAPIAppkeyAPI.as_view(), name="open_api_appkey_api"),
    url(r"^sso?$", SSOAPI.as_view(), name="sso_api")
]
