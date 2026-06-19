import logging
import re
import time
import uuid

from django.conf import settings
from django.contrib.auth import user_logged_in
from django.db import connection
from django.dispatch import receiver
from django.utils.timezone import now
from django.utils.deprecation import MiddlewareMixin

from utils.api import JSONResponse
from utils.observability_context import reset_request_id, set_request_id
from utils.observability_metrics import HTTP_REQUEST_DURATION_SECONDS, HTTP_REQUESTS_TOTAL
from account.models import User

request_logger = logging.getLogger("codeplace.request")
MAX_REQUEST_ID_LENGTH = 128
REQUEST_ID_ALLOWED_CHARS = re.compile(r"[^A-Za-z0-9_.:-]+")


class RequestIDMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = self._request_id(request)
        request.request_id = request_id
        token = set_request_id(request_id)
        try:
            response = self.get_response(request)
            response["X-Request-ID"] = request_id
            return response
        finally:
            reset_request_id(token)

    @staticmethod
    def _request_id(request):
        request_id = request.META.get("HTTP_X_REQUEST_ID")
        if not request_id:
            return uuid.uuid4().hex
        request_id = REQUEST_ID_ALLOWED_CHARS.sub("-", request_id).strip("-")
        if not request_id:
            return uuid.uuid4().hex
        return request_id[:MAX_REQUEST_ID_LENGTH]


class RequestLogMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started_at = time.monotonic()
        response = None
        try:
            response = self.get_response(request)
            return response
        finally:
            duration_seconds = time.monotonic() - started_at
            status_code = getattr(response, "status_code", 500)
            if request.path not in ("/metrics", "/api/health"):
                endpoint = self._endpoint(request)
                HTTP_REQUESTS_TOTAL.labels(request.method, endpoint, str(status_code)).inc()
                HTTP_REQUEST_DURATION_SECONDS.labels(request.method, endpoint).observe(duration_seconds)
                request_logger.info(
                    "request completed",
                    extra={
                        "request_id": getattr(request, "request_id", None),
                        "method": request.method,
                        "path": request.path,
                        "status_code": status_code,
                        "duration_ms": round(duration_seconds * 1000, 2),
                        "user_id": self._user_id(request),
                        "remote_addr": getattr(request, "ip", request.META.get(settings.IP_HEADER,
                                                                               request.META.get("REMOTE_ADDR"))),
                    },
                )

    @staticmethod
    def _endpoint(request):
        resolver_match = getattr(request, "resolver_match", None)
        if not resolver_match:
            return "unknown"
        return resolver_match.view_name or getattr(resolver_match, "route", None) or "unknown"

    @staticmethod
    def _user_id(request):
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            return getattr(user, "id", None)
        return None


class APITokenAuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        appkey = request.META.get("HTTP_APPKEY")
        if appkey:
            try:
                request.user = User.objects.get(open_api_appkey=appkey, open_api=True, is_disabled=False)
                request.csrf_processing_done = True
                request.auth_method = "api_key"
            except User.DoesNotExist:
                pass


class SessionRecordMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.ip = request.META.get(settings.IP_HEADER, request.META.get("REMOTE_ADDR"))
        if request.user.is_authenticated and request.session.session_key:
            session = request.session
            if 'user_agent' not in session or 'ip' not in session:
                session["user_agent"] = request.META.get("HTTP_USER_AGENT", "")
                session["ip"] = request.ip
                session.modified = True
            session["last_activity"] = now()
            session.save()


@receiver(user_logged_in)
def add_session_key(sender, request, user, **kwargs):
    if request.session.session_key and request.session.session_key not in user.session_keys:
        user.session_keys.append(request.session.session_key)
        user.save()


class AdminRoleRequiredMiddleware(MiddlewareMixin):

    def process_request(self, request):
        path = request.path_info
        if path.startswith("/admin/") or path.startswith("/api/admin/"):
            if not (request.user.is_authenticated and request.user.is_admin_role()):
                return JSONResponse.response({"error": "login-required", "data": "Please login in first"})


class LogSqlMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        print("\033[94m", "#" * 30, "\033[0m")
        time_threshold = 0.03
        for query in connection.queries:
            if float(query["time"]) > time_threshold:
                print("\033[93m", query, "\n", "-" * 30, "\033[0m")
            else:
                print(query, "\n", "-" * 30)
        return response
