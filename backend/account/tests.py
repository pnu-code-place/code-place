import time

from unittest import mock
from datetime import timedelta
from copy import deepcopy

from django.contrib import auth
from django.utils.timezone import now
from otpauth import OtpAuth

from utils.api.tests import APIClient, APITestCase
from utils.shortcuts import rand_str
from options.options import SysOptions

from .models import AdminType, ProblemPermission, User


class PermissionDecoratorTest(APITestCase):
    """
    데코레이터 테스트
    """
    def setUp(self):
        self.regular_user = User.objects.create(username="regular_user")
        self.admin = User.objects.create(username="admin")
        self.super_admin = User.objects.create(username="super_admin")
        self.request = mock.MagicMock()
        self.request.user.is_authenticated = mock.MagicMock()

    def test_login_required(self):
        self.request.user.is_authenticated.return_value = False

    def test_admin_required(self):
        pass

    def test_super_admin_required(self):
        pass


class DuplicateUserCheckAPITest(APITestCase):
    """
    닉네임 또는 이메일 유효성 검사 API 테스트
    """
    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.email = "test@test.com"
        self.username = "test"
        self.password = "test1234!"
        self.create_user(email=self.email, username=self.username, password=self.password, login=False)
        self.url = self.reverse("check_username_or_email")

    def test_duplicate_username(self):
        resp = self.client.post(self.url, data={"username": "test"})
        data = resp.data["data"]
        self.assertEqual(data["username"], True)
        resp = self.client.post(self.url, data={"username": "Test"})
        self.assertEqual(resp.data["data"]["username"], True)

    def test_ok_username(self):
        resp = self.client.post(self.url, data={"username": "test1"})
        data = resp.data["data"]
        self.assertFalse(data["username"])

    def test_duplicate_email(self):
        resp = self.client.post(self.url, data={"email": "test@test.com"})
        self.assertEqual(resp.data["data"]["email"], True)
        resp = self.client.post(self.url, data={"email": "Test@Test.com"})
        self.assertTrue(resp.data["data"]["email"])

    def test_ok_email(self):
        resp = self.client.post(self.url, data={"email": "aa@test.com"})
        self.assertFalse(resp.data["data"]["email"])

class UserLoginAPITest(APITestCase):
    """
    로그인 API 테스트
    """
    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.email = "test@test.com"
        self.username = "test"
        self.password = "test1234!"
        self.user = self.create_user(email=self.email, username=self.username, password=self.password, login=False)
        self.login_url = self.reverse("user_login_api")

    def test_login_with_correct_info(self):
        response = self.client.post(self.login_url, data={"username": self.email, "password": self.password})
        self.assertDictEqual(response.data, {"error": None, "data": "Succeeded"})

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_login_with_correct_info_upper_username(self):
        resp = self.client.post(self.login_url, data={"username": self.email.upper(), "password": self.password})
        self.assertDictEqual(resp.data, {"error": None, "data": "Succeeded"})
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_login_with_wrong_info(self):
        response = self.client.post(self.login_url,
                                           data={"username": self.email, "password": "invalid_password"})
        self.assertDictEqual(response.data, {"error": "error", "data": "Invalid username or password"})

        user = auth.get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_user_disabled(self):
        self.user.is_disabled = True
        self.user.save()
        resp = self.client.post(self.login_url, data={"username": self.email,
                                                      "password": self.password})
        self.assertDictEqual(resp.data, {"error": "error", "data": "Your account has been disabled"})


class CaptchaTest(APITestCase):
    def _set_captcha(self, session):
        captcha = rand_str(4)
        session["_django_captcha_key"] = captcha
        session["_django_captcha_expires_time"] = int(time.time()) + 30
        session.save()
        return captcha


class UserRegisterAPITest(CaptchaTest):
    def setUp(self):
        self.client = APIClient()
        self.register_url = self.reverse("user_register_api")
        self.email = "test@test.com"
        self.username = "test"
        self.password = "test1234!"
        self.create_school_fixtures(1, "Test", 1, "Test")
        self.data = {"email": "test@test.com", "password": "test1234!", "username": "test",
                     "real_name": "realname", "student_id":"202400000", "collegeId": 1, "departmentId": 1}

    def test_website_config_limit(self):
        SysOptions.allow_register = False
        resp = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Register function has been disabled by admin"})

    def test_register_with_correct_info(self):
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": None, "data": "Succeeded"})

    def test_username_already_exists(self):
        self.test_register_with_correct_info()
        self.data["username"] = "test"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": "nickname already exists"})

    def test_email_already_exists(self):
        self.test_register_with_correct_info()
        self.data["username"] = "user_2"
        self.data["email"] = "test@test.com"
        response = self.client.post(self.register_url, data=self.data)
        self.assertDictEqual(response.data, {"error": "error", "data": "email already exists"})


class SessionManagementAPITest(APITestCase):
    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.email = "test@test.com"
        self.username = "test"
        self.password = "test1234!"
        self.create_user(email=self.email, username=self.username, password=self.password, login=False)
        self.url = self.reverse("session_management_api")
        login_url = self.reverse("user_login_api")
        self.client.post(login_url, data={"username": self.email, "password": self.password})

    def test_get_sessions(self):
        resp = self.client.get(self.url)
        self.assertSuccess(resp)
        data = resp.data["data"]
        self.assertEqual(len(data), 1)

    def test_delete_session_with_invalid_key(self):
        resp = self.client.delete(self.url + "?session_key=aaaaaaaaaa")
        self.assertDictEqual(resp.data, {"error": "error", "data": "Invalid session_key"})

#
# class UserProfileAPITest(APITestCase):
#     def setUp(self):
#         self.url = self.reverse("user_profile_api")
#
#     def test_get_profile_without_login(self):
#         resp = self.client.get(self.url)
#         self.assertDictEqual(resp.data, {"error": None, "data": None})
#
#     def test_get_profile(self):
#         self.create_user("test", "test123")
#         resp = self.client.get(self.url)
#         self.assertSuccess(resp)
#
#     def test_update_profile(self):
#         self.create_user("test", "test123")
#         update_data = {"real_name": "zemal", "submission_number": 233, "language": "en-US"}
#         resp = self.client.put(self.url, data=update_data)
#         self.assertSuccess(resp)
#         data = resp.data["data"]
#         self.assertEqual(data["real_name"], "zemal")
#         self.assertEqual(data["submission_number"], 0)
#         self.assertEqual(data["language"], "en-US")

@mock.patch("account.views.oj.send_email_async.send")
class ApplyResetPasswordAPITest(CaptchaTest):
    """
    비밀번호 재설정 (로그인 전) 이메일 발송 API 테스트
    """
    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.email = "test@test.com"
        self.username = "test"
        self.password = "test1234!"
        self.create_user(email=self.email, username=self.username, password=self.password, login=False)
        self.url = self.reverse("apply_reset_password_api")
        self.data = {"email": "test@test.com", "captcha": self._set_captcha(self.client.session)}

    def _refresh_captcha(self):
        self.data["captcha"] = self._set_captcha(self.client.session)

    def test_apply_reset_password(self, send_email_send):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        send_email_send.assert_called()

    def test_apply_reset_password_twice_in_20_mins(self, send_email_send):
        self.test_apply_reset_password()
        send_email_send.reset_mock()
        self._refresh_captcha()
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "You can only reset password once per 20 minutes"})
        send_email_send.assert_not_called()

    def test_apply_reset_password_again_after_20_mins(self, send_email_send):
        self.test_apply_reset_password()
        user = User.objects.first()
        user.reset_password_token_expire_time = now() - timedelta(minutes=21)
        user.save()
        self._refresh_captcha()
        self.test_apply_reset_password()


class ResetPasswordAPITest(CaptchaTest):
    """
    비밀번호 재설정 (로그인 전) API 테스트
    """
    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.create_user(email="test@test.com", username="test", password="test1234!", login=False)
        self.url = self.reverse("reset_password_api")
        user = User.objects.first()
        user.reset_password_token = "online_judge?"
        user.reset_password_token_expire_time = now() + timedelta(minutes=20)
        user.save()
        self.data = {"token": user.reset_password_token,
                     "captcha": self._set_captcha(self.client.session),
                     "password": "test1111!"}

    def test_reset_password_with_invalid_password(self):
        # 8자보다 짧은 비밀번호
        self.data["password"] = "invalid"
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "invalid-password", "data": "password: Ensure this field has at least 8 characters."})
        # 특수문자 없는 비밀번호
        self.data["password"] = "aaaaa33234"
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "invalid-password", "data": "password: This value does not match the required pattern."})
        # 숫자 없는 비밀번호
        self.data["password"] = "aaaaa!!!!!"
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "invalid-password", "data": "password: This value does not match the required pattern."})

    def test_reset_password_with_correct_token(self):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        self.assertTrue(self.client.login(username="test@test.com", password="test1111!"))

    def test_reset_password_with_invalid_token(self):
        self.data["token"] = "aaaaaaaaaaa"
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Token does not exist"})

    def test_reset_password_with_expired_token(self):
        user = User.objects.first()
        user.reset_password_token_expire_time = now() - timedelta(seconds=30)
        user.save()
        resp = self.client.post(self.url, data=self.data)
        self.assertDictEqual(resp.data, {"error": "error", "data": "Token has expired"})



class GenerateUserAPITest(APITestCase):
    def setUp(self):
        self.create_school_fixtures(college_id=1, college_name="Test", department_id=1, department_name="Test")
        self.create_super_admin()
        self.url = self.reverse("generate_user_api")
        self.data = {
            "college": 1,
            "department": 1,
            "prefix": "pre",
            "num_of_mock": 10,
        }

    def test_error_case(self):
        data = deepcopy(self.data)
        data["prefix"] = "a" * 11
        resp = self.client.post(self.url, data=data)
        self.assertEqual(resp.data["data"], "prefix: Ensure this field has no more than 10 characters.")

        data2 = deepcopy(self.data)
        data2["num_of_mock"] = 21
        resp = self.client.post(self.url, data=data2)
        self.assertEqual(resp.data["data"], "num_of_mock: Ensure this value is less than or equal to 20.")

    @mock.patch("account.views.admin.xlsxwriter.Workbook")
    def test_generate_user_success(self, mock_workbook):
        resp = self.client.post(self.url, data=self.data)
        self.assertSuccess(resp)
        mock_workbook.assert_called()

# class UserChangePasswordAPITest(APITestCase):
#     def setUp(self):
#         self.url = self.reverse("user_change_password_api")
#
#         # Create user at first
#         self.username = "test_user"
#         self.old_password = "testuserpassword"
#         self.new_password = "new_password"
#         self.user = self.create_user(username=self.username, password=self.old_password, login=False)
#
#         self.data = {"old_password": self.old_password, "new_password": self.new_password}
#
#     def _get_tfa_code(self):
#         user = User.objects.first()
#         code = OtpAuth(user.tfa_token).totp()
#         if len(str(code)) < 6:
#             code = (6 - len(str(code))) * "0" + str(code)
#         return code
#
#     def test_login_required(self):
#         response = self.client.post(self.url, data=self.data)
#         self.assertEqual(response.data, {"error": "permission-denied", "data": "Please login first"})
#
#     def test_valid_ola_password(self):
#         self.assertTrue(self.client.login(username=self.username, password=self.old_password))
#         response = self.client.post(self.url, data=self.data)
#         self.assertEqual(response.data, {"error": None, "data": "Succeeded"})
#         self.assertTrue(self.client.login(username=self.username, password=self.new_password))
#
#     def test_invalid_old_password(self):
#         self.assertTrue(self.client.login(username=self.username, password=self.old_password))
#         self.data["old_password"] = "invalid"
#         response = self.client.post(self.url, data=self.data)
#         self.assertEqual(response.data, {"error": "error", "data": "Invalid old password"})
#
#     def test_tfa_code_required(self):
#         self.user.two_factor_auth = True
#         self.user.tfa_token = "tfa_token"
#         self.user.save()
#         self.assertTrue(self.client.login(username=self.username, password=self.old_password))
#         self.data["tfa_code"] = rand_str(6)
#         resp = self.client.post(self.url, data=self.data)
#         self.assertEqual(resp.data, {"error": "error", "data": "Invalid two factor verification code"})
#
#         self.data["tfa_code"] = self._get_tfa_code()
#         resp = self.client.post(self.url, data=self.data)
#         self.assertSuccess(resp)

#
# class UserRankAPITest(APITestCase):
#     def setUp(self):
#         self.url = self.reverse("user_rank_api")
#         self.create_user("test1", "test123", login=False)
#         self.create_user("test2", "test123", login=False)
#         test1 = User.objects.get(username="test1")
#         profile1 = test1.userprofile
#         profile1.submission_number = 10
#         profile1.accepted_number = 10
#         profile1.total_score = 240
#         profile1.save()
#
#         test2 = User.objects.get(username="test2")
#         profile2 = test2.userprofile
#         profile2.submission_number = 15
#         profile2.accepted_number = 10
#         profile2.total_score = 700
#         profile2.save()
#
#     def test_get_acm_rank(self):
#         resp = self.client.get(self.url, data={"rule": ContestRuleType.ACM})
#         self.assertSuccess(resp)
#         data = resp.data["data"]["results"]
#         self.assertEqual(data[0]["user"]["username"], "test1")
#         self.assertEqual(data[1]["user"]["username"], "test2")
#
#     def test_get_oi_rank(self):
#         resp = self.client.get(self.url, data={"rule": ContestRuleType.OI})
#         self.assertSuccess(resp)
#         data = resp.data["data"]["results"]
#         self.assertEqual(data[0]["user"]["username"], "test2")
#         self.assertEqual(data[1]["user"]["username"], "test1")
#
#     def test_admin_role_filted(self):
#         self.create_admin("admin", "admin123")
#         admin = User.objects.get(username="admin")
#         profile1 = admin.userprofile
#         profile1.submission_number = 20
#         profile1.accepted_number = 5
#         profile1.total_score = 300
#         profile1.save()
#         resp = self.client.get(self.url, data={"rule": ContestRuleType.ACM})
#         self.assertSuccess(resp)
#         self.assertEqual(len(resp.data["data"]), 2)
#
#         resp = self.client.get(self.url, data={"rule": ContestRuleType.OI})
#         self.assertSuccess(resp)
#         self.assertEqual(len(resp.data["data"]), 2)


#
#
# class AdminUserTest(APITestCase):
#     def setUp(self):
#         self.user = self.create_super_admin(login=True)
#         self.username = self.password = "test"
#         self.regular_user = self.create_user(username=self.username, password=self.password, login=False)
#         self.url = self.reverse("user_admin_api")
#         self.data = {"id": self.regular_user.id, "username": self.username, "real_name": "test_name",
#                      "email": "test@qq.com", "admin_type": AdminType.REGULAR_USER,
#                      "problem_permission": ProblemPermission.OWN, "open_api": True,
#                      "two_factor_auth": False, "is_disabled": False}
#
#     def test_user_list(self):
#         response = self.client.get(self.url)
#         self.assertSuccess(response)
#
#     def test_edit_user_successfully(self):
#         response = self.client.put(self.url, data=self.data)
#         self.assertSuccess(response)
#         resp_data = response.data["data"]
#         self.assertEqual(resp_data["username"], self.username)
#         self.assertEqual(resp_data["email"], "test@qq.com")
#         self.assertEqual(resp_data["open_api"], True)
#         self.assertEqual(resp_data["two_factor_auth"], False)
#         self.assertEqual(resp_data["is_disabled"], False)
#         self.assertEqual(resp_data["problem_permission"], ProblemPermission.NONE)
#
#         self.assertTrue(self.regular_user.check_password("test"))
#
#     def test_edit_user_password(self):
#         data = self.data
#         new_password = "testpassword"
#         data["password"] = new_password
#         response = self.client.put(self.url, data=data)
#         self.assertSuccess(response)
#         user = User.objects.get(id=self.regular_user.id)
#         self.assertFalse(user.check_password(self.password))
#         self.assertTrue(user.check_password(new_password))
#
#     def test_edit_user_tfa(self):
#         data = self.data
#         self.assertIsNone(self.regular_user.tfa_token)
#         data["two_factor_auth"] = True
#         response = self.client.put(self.url, data=data)
#         self.assertSuccess(response)
#         resp_data = response.data["data"]
#         # if `tfa_token` is None, a new value will be generated
#         self.assertTrue(resp_data["two_factor_auth"])
#         token = User.objects.get(id=self.regular_user.id).tfa_token
#         self.assertIsNotNone(token)
#
#         response = self.client.put(self.url, data=data)
#         self.assertSuccess(response)
#         resp_data = response.data["data"]
#         # if `tfa_token` is not None, the value is not changed
#         self.assertTrue(resp_data["two_factor_auth"])
#         self.assertEqual(User.objects.get(id=self.regular_user.id).tfa_token, token)
#
#     def test_edit_user_openapi(self):
#         data = self.data
#         self.assertIsNone(self.regular_user.open_api_appkey)
#         data["open_api"] = True
#         response = self.client.put(self.url, data=data)
#         self.assertSuccess(response)
#         resp_data = response.data["data"]
#         # if `open_api_appkey` is None, a new value will be generated
#         self.assertTrue(resp_data["open_api"])
#         key = User.objects.get(id=self.regular_user.id).open_api_appkey
#         self.assertIsNotNone(key)
#
#         response = self.client.put(self.url, data=data)
#         self.assertSuccess(response)
#         resp_data = response.data["data"]
#         # if `openapi_app_key` is not None, the value is not changed
#         self.assertTrue(resp_data["open_api"])
#         self.assertEqual(User.objects.get(id=self.regular_user.id).open_api_appkey, key)
#
#     def test_import_users(self):
#         data = {"users": [["user1", "pass1", "eami1@e.com", "user1"],
#                           ["user2", "pass3", "eamil3@e.com", "user2"]]
#                 }
#         resp = self.client.post(self.url, data)
#         self.assertSuccess(resp)
#         # successfully created 2 users
#         self.assertEqual(User.objects.all().count(), 4)
#
#     def test_import_duplicate_user(self):
#         data = {"users": [["user1", "pass1", "eami1@e.com", "user1"],
#                           ["user1", "pass1", "eami1@e.com", "user1"]]
#                 }
#         resp = self.client.post(self.url, data)
#         self.assertFailed(resp, "DETAIL:  Key (username)=(user1) already exists.")
#         # no user is created
#         self.assertEqual(User.objects.all().count(), 2)
#
#     def test_delete_users(self):
#         self.test_import_users()
#         user_ids = User.objects.filter(username__in=["user1", "user2"]).values_list("id", flat=True)
#         user_ids = ",".join([str(id) for id in user_ids])
#         resp = self.client.delete(self.url + "?id=" + user_ids)
#         self.assertSuccess(resp)
#         self.assertEqual(User.objects.all().count(), 2)
