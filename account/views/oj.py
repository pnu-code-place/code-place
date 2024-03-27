import os
from datetime import timedelta
from importlib import import_module
import json

import qrcode
from django.conf import settings
from django.contrib import auth
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from otpauth import OtpAuth
from django.core.cache import cache
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden, HttpResponseServerError
from django.db.models import F, Count, Q
from django.db import transaction

from problem.models import Problem
from utils.constants import ContestRuleType
from options.options import SysOptions
from utils.api import APIView, validate_serializer, CSRFExemptAPIView
from utils.captcha import Captcha
from utils.shortcuts import rand_str, img2base64, datetime2str
from ..decorators import login_required
from ..models import User, UserProfile, AdminType, College, Department, UserScore, UserSolved
from ..serializers import (ApplyResetPasswordSerializer, ResetPasswordSerializer,
                           UserChangePasswordSerializer, UserLoginSerializer,
                           UserRegisterSerializer, UsernameOrEmailCheckSerializer,
                           RankInfoSerializer, UserChangeEmailSerializer, SSOSerializer,
                           CollegeListSerializer, DepartmentSerializer, RankingSerializer,
                           DashboardSubmissionSerializer,
                           DashboardDepartmentSerializer, DashboardCollegeSerializer, DashboardRankSerializer,
                           HomeRankingSerializer)
from ..serializers import (TwoFactorAuthCodeSerializer, UserProfileSerializer,
                           EditUserProfileSerializer, ImageUploadForm)
from ..tasks import send_email_async


class GetCollegeListAPI(APIView):
    def get(self, request):
        try:
            college_list = College.objects.all()
        except College.DoesNotExist:
            return self.error("failed to get college list")
        return self.success(CollegeListSerializer(college_list, many=True).data)


class GetDepartmentListAPI(APIView):
    def get(self, request):
        try:
            college_id = request.GET.get("college_id")
            department_list = Department.objects.filter(college=college_id).order_by('id')
        except Department.DoesNotExist:
            return self.error("failed to get department list")
        return self.success(DepartmentSerializer(department_list, many=True).data)


class GetRankingAPI(APIView):
    def get(self, request):
        try:
            limit = int(request.GET.get("limit", None))
            if limit:
                ranking = UserScore.objects.all().order_by('-score')[:limit]
            else:
                ranking = UserScore.objects.all().order_by('-score')
            return self.success(RankingSerializer(ranking, many=True).data)
        except UserScore.DoesNotExist:
            return HttpResponseNotFound("no ranking table")


class UserProfileAPI(APIView):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, **kwargs):
        """
        判断是否登录， 若登录返回用户信息
        """
        user = request.user
        if not user.is_authenticated:
            return self.success()
        show_real_name = False
        username = request.GET.get("username")
        try:
            if username:
                user = User.objects.get(username=username, is_disabled=False)
            else:
                user = request.user
                # api返回的是自己的信息，可以返real_name
                show_real_name = True
        except User.DoesNotExist:
            return self.error("User does not exist")
        return self.success(UserProfileSerializer(user.userprofile, show_real_name=show_real_name).data)

    @validate_serializer(EditUserProfileSerializer)
    @login_required
    def put(self, request):
        data = request.data
        user_profile = request.user.userprofile
        for k, v in data.items():
            setattr(user_profile, k, v)
        user_profile.save()
        return self.success(UserProfileSerializer(user_profile, show_real_name=True).data)


# class UserProfileDashBoardAPI(APIView):
#     @login_required
#     def get(self, request):
#         try:
#             user_id = request.user.id
#             user = User.objects.filter(id=user_id).first()
#             user_profile = UserProfile.objects.filter(user_id=user_id).first()
#             user_department = Department.objects.filter(id=user_profile.department_id).first()
#             user_college = College.objects.filter(id=user_profile.college_id).first()
#             user_score = UserScore.objects.filter(user_id=user_id).annotate(
#                 total_rank=Count('total_score',
#                                  filter=Q(total_score__gt=F('total_score'))) + 1,
#                 datastructure_rank=Count('datastructure_score',
#                                          filter=Q(datastructure_score__gt=F('datastructure_score'))) + 1,
#                 implementation_rank=Count('implementation_score',
#                                           filter=Q(implementation_score__gt=F('implementation_score'))) + 1,
#                 math_rank=Count('math_score',
#                                 filter=Q(math_score__gt=F('math_score'))) + 1,
#                 search_rank=Count('search_score',
#                                   filter=Q(search_score__gt=F('search_score'))) + 1,
#                 sorting_rank=Count('sorting_score',
#                                    filter=Q(search_score__gt=F('sorting_score'))) + 1
#             ).first()
#         except User.DoesNotExist or UserProfile.DoesNotExist:
#             return HttpResponseNotFound('user does not exist')
#         except Department.DoesNotExist or College.DoesNotExist:
#             return HttpResponseNotFound('department or college does not exist')
#         except UserScore.DoesNotExist:
#             return HttpResponseNotFound('user_score does not exist')
#
#         total_user_count = UserScore.objects.count()
#
#         oj_status = {}
#         oj_status.update(DashboardUserInfoSerializer(user).data)
#         oj_status.update(DashboardSubmissionSerializer(user_profile).data)
#         oj_status.update(DashboardDepartmentSerializer(user_department).data)
#         oj_status.update(DashboardCollegeSerializer(user_college).data)
#         oj_status.update(DashboardRankSerializer(user_score, context={'total_user_count': total_user_count}).data)
#
#         return self.success(oj_status)


class HomeRankingAPI(APIView):
    def get(self, request):
        # rank, avatar, tier, total_score, fluctuation
        limit = request.GET.get('limit', 100)
        try:
            ranking = UserScore.objects.all().order_by('-total_score')[:limit]
        except UserScore.DoesNotExist:
            return HttpResponseNotFound('no user score table')
        return self.success(HomeRankingSerializer(ranking, many=True).data)


class AvatarUploadAPI(APIView):
    request_parsers = ()

    @login_required
    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            avatar = form.cleaned_data["image"]
        else:
            return self.error("Invalid file content")
        if avatar.size > 2 * 1024 * 1024:
            return self.error("Picture is too large")
        suffix = os.path.splitext(avatar.name)[-1].lower()
        if suffix not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
            return self.error("Unsupported file format")

        name = rand_str(10) + suffix
        with open(os.path.join(settings.AVATAR_UPLOAD_DIR, name), "wb") as img:
            for chunk in avatar:
                img.write(chunk)
        user_profile = request.user.userprofile

        user_profile.avatar = f"{settings.AVATAR_URI_PREFIX}/{name}"
        user_profile.save()
        return self.success("Succeeded")


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
        result = {
            "username": False,
            "email": False
        }
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

        code = rand_str(6)
        # key: 이메일, value: 코드값(6자리), timeout=5분
        cache.set(email, code, timeout=60 * 5)

        email_html = render_to_string("email_valid_email.html", {'code': code})
        send_email_async.send(from_name=SysOptions.website_name_shortcut,
                              to_email=email,
                              to_name=email,
                              subject="[PNU Online Judge] 이메일 확인 인증번호입니다.",
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


class UserRegisterAPI(APIView):
    @validate_serializer(UserRegisterSerializer)
    def post(self, request):
        """
        User register api
        """
        if not SysOptions.allow_register:
            return self.error("Register function has been disabled by admin")

        data = request.data
        print(data)
        data["username"] = data["username"].lower()
        data["email"] = data["email"].lower()

        if User.objects.filter(username=data["username"]).exists():
            return self.error("username already exists")
        if User.objects.filter(email=data["email"]).exists():
            return self.error("email already exists")
        print(data)
        college = College.objects.get(id=data['collegeId'])
        department = Department.objects.get(id=data['departmentId'])
        with transaction.atomic():
            user = User.objects.create(username=data["username"], email=data["email"])
            user.set_password(data["password"])
            user.save()
            user_profile = UserProfile.objects.create(user=user, college=college, department=department)
            user_profile.save()
            user_score = UserScore.objects.create(user=user)
            user_score.save()
            user_solved = UserSolved.objects.create(user=user)
            user_solved.save()
        return self.success("Succeeded")


class UserChangeEmailAPI(APIView):
    @validate_serializer(UserChangeEmailSerializer)
    @login_required
    def post(self, request):
        data = request.data
        user = auth.authenticate(username=request.user.username, password=data["password"])
        if user:
            if user.two_factor_auth:
                if "tfa_code" not in data:
                    return self.error("tfa_required")
                if not OtpAuth(user.tfa_token).valid_totp(data["tfa_code"]):
                    return self.error("Invalid two factor verification code")
            data["new_email"] = data["new_email"].lower()
            if User.objects.filter(email=data["new_email"]).exists():
                return self.error("The email is owned by other account")
            user.email = data["new_email"]
            user.save()
            return self.success("Succeeded")
        else:
            return self.error("Wrong password")


class UserChangePasswordAPI(APIView):
    @validate_serializer(UserChangePasswordSerializer)
    @login_required
    def post(self, request):
        """
        User change password api
        """
        data = request.data
        username = request.user.username
        user = auth.authenticate(username=username, password=data["old_password"])
        if user:
            if user.two_factor_auth:
                if "tfa_code" not in data:
                    return self.error("tfa_required")
                if not OtpAuth(user.tfa_token).valid_totp(data["tfa_code"]):
                    return self.error("Invalid two factor verification code")
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
        send_email_async.send(from_name=SysOptions.website_name_shortcut,
                              to_email=user.email,
                              to_name=user.username,
                              subject="Reset your password",
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


class UserRankAPI(APIView):
    def get(self, request):
        rule_type = request.GET.get("rule")
        if rule_type not in ContestRuleType.choices():
            rule_type = ContestRuleType.ACM
        profiles = UserProfile.objects.filter(user__admin_type=AdminType.REGULAR_USER, user__is_disabled=False) \
            .select_related("user")
        if rule_type == ContestRuleType.ACM:
            profiles = profiles.filter(submission_number__gt=0).order_by("-accepted_number", "submission_number")
        else:
            profiles = profiles.filter(total_score__gt=0).order_by("-total_score")
        return self.success(self.paginate_data(request, profiles, RankInfoSerializer))


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
        return self.success(
            {"username": user.username, "avatar": user.userprofile.avatar, "admin_type": user.admin_type})
