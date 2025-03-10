import os
from datetime import timedelta
from importlib import import_module
import json

import qrcode
from django.conf import settings
from django.contrib import auth
from django.db.models.functions import Concat
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from otpauth import OtpAuth
from django.core.cache import cache
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden, HttpResponseServerError, \
    JsonResponse
from django.db.models import F, Count, Q, Sum, Value, TextField
from django.db import transaction

from contest.models import Contest
from problem.models import Problem
from school.models import College, Department
from utils.constants import ContestRuleType, UNDEFINED_SMTP_USER
from options.options import SysOptions
from utils.api import APIView, validate_serializer, CSRFExemptAPIView
from utils.captcha import Captcha
from utils.shortcuts import rand_str, img2base64, datetime2str
from ..decorators import login_required
from ..models import User, UserProfile, AdminType, UserScore, UserSolved
from ..serializers import (ApplyResetPasswordSerializer, ResetPasswordSerializer, UserChangePasswordSerializer,
                           UserLoginSerializer, UserRegisterSerializer, UsernameOrEmailCheckSerializer,
                           RankInfoSerializer, SSOSerializer)
from ..serializers import TwoFactorAuthCodeSerializer
from ..tasks import send_email_async


class TwoFactorAuthAPI(APIView):

    @login_required
    def get(self, request):
        """
        Get QR code
        """
        user = request.user
        if user.two_factor_auth:
            return self.error("2FA is already turned on")
        token = rand_str()
        user.tfa_token = token
        user.save()

        label = f"{SysOptions.website_name_shortcut}:{user.username}"
        image = qrcode.make(OtpAuth(token).to_uri("totp", label, SysOptions.website_name.replace(" ", "")))
        return self.success(img2base64(image))

    @login_required
    @validate_serializer(TwoFactorAuthCodeSerializer)
    def post(self, request):
        """
        Open 2FA
        """
        code = request.data["code"]
        user = request.user
        if OtpAuth(user.tfa_token).valid_totp(code):
            user.two_factor_auth = True
            user.save()
            return self.success("Succeeded")
        else:
            return self.error("Invalid code")

    @login_required
    @validate_serializer(TwoFactorAuthCodeSerializer)
    def put(self, request):
        code = request.data["code"]
        user = request.user
        if not user.two_factor_auth:
            return self.error("2FA is already turned off")
        if OtpAuth(user.tfa_token).valid_totp(code):
            user.two_factor_auth = False
            user.save()
            return self.success("Succeeded")
        else:
            return self.error("Invalid code")


class CheckTFARequiredAPI(APIView):

    @validate_serializer(UsernameOrEmailCheckSerializer)
    def post(self, request):
        """
        Check TFA is required
        """
        data = request.data
        result = False
        if data.get("username"):
            try:
                user = User.objects.get(username=data["username"])
                result = user.two_factor_auth
            except User.DoesNotExist:
                pass
        return self.success({"result": result})


class UserLoginAPI(APIView):

    @validate_serializer(UserLoginSerializer)
    def post(self, request):
        """
        User login api
        """
        data = request.data
        user = auth.authenticate(username=data["username"], password=data["password"])
        # None is returned if username or password is wrong
        if user:
            if user.is_disabled:
                return self.error("Your account has been disabled")
            if not user.two_factor_auth:
                auth.login(request, user)
                return self.success("Succeeded")

            # `tfa_code` not in post data
            if user.two_factor_auth and "tfa_code" not in data:
                return self.error("tfa_required")

            if OtpAuth(user.tfa_token).valid_totp(data["tfa_code"]):
                auth.login(request, user)
                return self.success("Succeeded")
            else:
                return self.error("Invalid two factor verification code")
        else:
            return self.error("Invalid username or password")


class UserLogoutAPI(APIView):

    def get(self, request):
        auth.logout(request)
        return self.success()


class UsernameOrEmailCheck(APIView):

    @validate_serializer(UsernameOrEmailCheckSerializer)
    def post(self, request):
        """
        check username or email is duplicate
        """
        data = request.data
        # True means already exist.
        result = {"username": False, "email": False}
        if data.get("username"):
            result["username"] = User.objects.filter(username=data["username"].lower()).exists()
        if data.get("email"):
            result["email"] = User.objects.filter(email=data["email"].lower()).exists()
        return self.success(result)


class ApplyUserEmailValidCheckAPI(APIView):

    def post(self, request):
        data = request.data
        if not data.get("email"):
            return HttpResponseBadRequest("no email in body")

        email = data["email"]

        if User.objects.filter(email=email).exists():
            return HttpResponseBadRequest("email already exists")

        code = rand_str(6)
        # key: 이메일, value: 코드값(6자리), timeout=5분
        cache.set(email, code, timeout=60 * 5)

        email_html = render_to_string("email_valid_email.html", {'code': code})
        send_email_async.send(
            from_name=SysOptions.website_name_shortcut,
            to_email=email,
            to_name=UNDEFINED_SMTP_USER,
            subject="[부산대학교 코드플레이스] 이메일 확인 인증번호입니다.",
            content=email_html)
        return self.success('email validation code sent')


class UserEmailValidCheckAPI(APIView):

    def post(self, request):
        data = request.data

        if not data.get('email'):
            return HttpResponseBadRequest('no email in request data')
        if not data.get('code'):
            return HttpResponseBadRequest('no code in request data')

        email = data["email"]
        code = data["code"]

        if not cache.get(email):
            return HttpResponseServerError("code expired or invalid email")

        valid_code = cache.get(email)
        if code == valid_code:
            cache.delete(email)
            print("code validation complete")
            return self.success('user email validation complete')
        else:
            return HttpResponseServerError("validation code mismatch")


class NicknameValidCheckAPI(APIView):

    def get(self, request):
        nickname = request.GET.get("nickname")
        if not nickname:
            return HttpResponseBadRequest('no nickname in request')
        if User.objects.filter(username=nickname).exists():
            return HttpResponseBadRequest('nickname already exists')
        return self.success("nickname validation complete")


class UserRegisterAPI(APIView):

    @validate_serializer(UserRegisterSerializer)
    def post(self, request):
        """
        User register api
        """
        if not SysOptions.allow_register:
            return self.error("Register function has been disabled by admin")

        data = request.data
        data["username"] = data["username"].lower()
        data["email"] = data["email"].lower()

        # 중복 체크
        if User.objects.filter(username=data["username"]).exists():
            return self.error("nickname already exists")
        if User.objects.filter(email=data["email"]).exists():
            return self.error("email already exists")

        college = College.objects.get(id=data['collegeId'])
        department = Department.objects.get(id=data['departmentId'])

        with transaction.atomic():
            user = User.objects.create(username=data["username"], email=data["email"])
            user.set_password(data["password"])
            user.save()
            user_profile = UserProfile.objects.create(
                user=user,
                school=college.college_name,
                major=department.department_name,
                college=college,
                department=department,
                real_name=data["real_name"],
                student_id=data["student_id"])
            user_profile.save()
            user_score = UserScore.objects.create(user=user)
            user_score.save()
            user_solved = UserSolved.objects.create(user=user)
            user_solved.save()
        return self.success("Succeeded")


class UserChangePasswordAPI(APIView):

    @validate_serializer(UserChangePasswordSerializer)
    @login_required
    def post(self, request):
        """
        User change password api
        """
        data = request.data
        username = request.user.email
        user = auth.authenticate(username=username, password=data["old_password"])
        if user:
            user.set_password(data["new_password"])
            user.save()
            return self.success("Succeeded")
        else:
            return self.error("Invalid old password")


class ApplyResetPasswordAPI(APIView):

    @validate_serializer(ApplyResetPasswordSerializer)
    def post(self, request):
        if request.user.is_authenticated:
            return self.error("You have already logged in, are you kidding me? ")
        data = request.data
        captcha = Captcha(request)
        if not captcha.check(data["captcha"]):
            return self.error("Invalid captcha")
        try:
            print("validate user existance")
            user = User.objects.get(email__iexact=data["email"])
        except User.DoesNotExist:
            return self.error("User does not exist")
        if user.reset_password_token_expire_time and 0 < int(
            (user.reset_password_token_expire_time - now()).total_seconds()) < 20 * 60:
            return self.error("You can only reset password once per 20 minutes")
        user.reset_password_token = rand_str()
        user.reset_password_token_expire_time = now() + timedelta(minutes=20)
        user.save()
        render_data = {
            "username": user.username,
            "website_name": SysOptions.website_name,
            "link": f"{SysOptions.website_base_url}/reset-password/{user.reset_password_token}"
        }
        email_html = render_to_string("reset_password_email.html", render_data)
        send_email_async.send(
            from_name=SysOptions.website_name_shortcut,
            to_email=user.email,
            to_name=user.username,
            subject="CSEP 비밀번호 재설정 요청",
            content=email_html)
        return self.success("Succeeded")


class ResetPasswordAPI(APIView):

    @validate_serializer(ResetPasswordSerializer)
    def post(self, request):
        data = request.data
        captcha = Captcha(request)
        if not captcha.check(data["captcha"]):
            return self.error("Invalid captcha")
        try:
            user = User.objects.get(reset_password_token=data["token"])
        except User.DoesNotExist:
            return self.error("Token does not exist")
        if user.reset_password_token_expire_time < now():
            return self.error("Token has expired")
        user.reset_password_token = None
        user.two_factor_auth = False
        user.set_password(data["password"])
        user.save()
        return self.success("Succeeded")


class SessionManagementAPI(APIView):

    @login_required
    def get(self, request):
        engine = import_module(settings.SESSION_ENGINE)
        session_store = engine.SessionStore
        current_session = request.session.session_key
        session_keys = request.user.session_keys

        result = []
        modified = False
        for key in session_keys[:]:
            session = session_store(key)
            # session does not exist or is expiry
            if not session._session:
                session_keys.remove(key)
                modified = True
                continue
            s = {}
            if current_session == key:
                s["current_session"] = True
            s["ip"] = session["ip"]
            s["user_agent"] = session["user_agent"]
            s["last_activity"] = datetime2str(session["last_activity"])
            s["session_key"] = key
            result.append(s)
        if modified:
            request.user.save()
        return self.success(result)

    @login_required
    def delete(self, request):
        session_key = request.GET.get("session_key")
        if not session_key:
            return self.error("Parameter Error")
        request.session.delete(session_key)
        if session_key in request.user.session_keys:
            request.user.session_keys.remove(session_key)
            request.user.save()
            return self.success("Succeeded")
        else:
            return self.error("Invalid session_key")


class ProfileProblemDisplayIDRefreshAPI(APIView):

    @login_required
    def get(self, request):
        profile = request.user.userprofile
        acm_problems = profile.acm_problems_status.get("problems", {})
        oi_problems = profile.oi_problems_status.get("problems", {})
        ids = list(acm_problems.keys()) + list(oi_problems.keys())
        if not ids:
            return self.success()
        display_ids = Problem.objects.filter(id__in=ids, visible=True).values_list("_id", flat=True)
        id_map = dict(zip(ids, display_ids))
        for k, v in acm_problems.items():
            v["_id"] = id_map[k]
        for k, v in oi_problems.items():
            v["_id"] = id_map[k]
        profile.save(update_fields=["acm_problems_status", "oi_problems_status"])
        return self.success()


class OpenAPIAppkeyAPI(APIView):

    @login_required
    def post(self, request):
        user = request.user
        if not user.open_api:
            return self.error("OpenAPI function is truned off for you")
        api_appkey = rand_str()
        user.open_api_appkey = api_appkey
        user.save()
        return self.success({"appkey": api_appkey})


class SSOAPI(CSRFExemptAPIView):

    @login_required
    def get(self, request):
        token = rand_str()
        request.user.auth_token = token
        request.user.save()
        return self.success({"token": token})

    @method_decorator(csrf_exempt)
    @validate_serializer(SSOSerializer)
    def post(self, request):
        try:
            user = User.objects.get(auth_token=request.data["token"])
        except User.DoesNotExist:
            return self.error("User does not exist")
        return self.success({
            "username": user.username,
            "avatar": user.userprofile.avatar,
            "admin_type": user.admin_type
        })
