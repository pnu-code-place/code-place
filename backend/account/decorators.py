import functools
import hashlib
import time
import os

from problem.models import Problem
from contest.models import Contest, ContestType, ContestStatus, ContestRuleType
from utils.api import JSONResponse, APIError
from utils.constants import CONTEST_PASSWORD_SESSION_KEY
from .models import ProblemPermission


class BasePermissionDecorator(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, obj_type):
        return functools.partial(self.__call__, obj)

    def error(self, data):
        return JSONResponse.response({"error": "permission-denied", "data": data})

    def __call__(self, *args, **kwargs):
        self.request = args[1]

        if self.check_permission():
            if self.request.user.is_disabled:
                return self.error("Your account is disabled")
            return self.func(*args, **kwargs)
        else:
            return self.error("Please login first")

    def check_permission(self):
        raise NotImplementedError()


class login_required(BasePermissionDecorator):

    def check_permission(self):
        return self.request.user.is_authenticated


class super_admin_required(BasePermissionDecorator):

    def check_permission(self):
        user = self.request.user
        return user.is_authenticated and user.is_super_admin()


class admin_role_required(BasePermissionDecorator):

    def check_permission(self):
        user = self.request.user
        return user.is_authenticated and user.is_admin_role()


class problem_permission_required(admin_role_required):

    def check_permission(self):
        if not super(problem_permission_required, self).check_permission():
            return False
        if self.request.user.problem_permission == ProblemPermission.NONE:
            return False
        return True


def check_contest_password(password, contest_password):
    if not (password and contest_password):
        return False
    if password == contest_password:
        return True
    else:
        # sig#timestamp 这种形式的密码也可以，但是在界面上没提供支持
        # sig = sha256(contest_password + timestamp)[:8]
        if "#" in password:
            s = password.split("#")
            if len(s) != 2:
                return False
            sig, ts = s[0], s[1]

            if sig == hashlib.sha256((contest_password + ts).encode("utf-8")).hexdigest()[:8]:
                try:
                    ts = int(ts)
                except Exception:
                    return False
                return int(time.time()) < ts
            else:
                return False
        else:
            return False


def check_contest_permission(check_type="details"):
    """
    只供Class based view 使用，检查用户是否有权进入该contest, check_type 可选 details, problems, ranks, submissions
    若通过验证，在view中可通过self.contest获得该contest
    """

    def decorator(func):

        def _check_permission(*args, **kwargs):
            self = args[0]
            request = args[1]
            user = request.user
            if request.data.get("contest_id"):
                contest_id = request.data["contest_id"]
            else:
                contest_id = request.GET.get("contest_id")
            if not contest_id:
                return self.error("Parameter error, contest_id is required")

            try:
                # use self.contest to avoid query contest again in view.
                self.contest = Contest.objects.select_related("created_by").get(id=contest_id, visible=True)
            except Contest.DoesNotExist:
                return self.error("Contest %s doesn't exist" % contest_id)

            # Anonymous
            if not user.is_authenticated:
                return self.error("Please login first.")

            # creator or owner
            if user.is_contest_admin(self.contest):
                return func(*args, **kwargs)

            if self.contest.contest_type == ContestType.PASSWORD_PROTECTED_CONTEST:
                # password error
                if not check_contest_password(
                        request.session.get(CONTEST_PASSWORD_SESSION_KEY, {}).get(self.contest.id),
                        self.contest.password):
                    return self.error("Wrong password or password expired")

            # regular user get contest problems, ranks etc. before contest started
            if self.contest.status == ContestStatus.CONTEST_NOT_START and check_type != "details":
                return self.error("Contest has not started yet.")

            # check does user have permission to get ranks, submissions in OI Contest
            if self.contest.status == ContestStatus.CONTEST_UNDERWAY and self.contest.rule_type == ContestRuleType.OI:
                if not self.contest.real_time_rank and (check_type == "ranks" or check_type == "submissions"):
                    return self.error(f"No permission to get {check_type}")

            return func(*args, **kwargs)

        return _check_permission

    return decorator


def ensure_created_by(obj, user):
    e = APIError(msg=f"{obj.__class__.__name__} does not exist")
    if not user.is_admin_role():
        raise e
    if user.is_super_admin():
        return
    if isinstance(obj, Problem):
        if not user.can_mgmt_all_problem() and obj.created_by != user:
            raise e
    elif obj.created_by != user:
        raise e


class SchedulerOnlyDecorator(object):
    """Decorator class that restricts API access to requests with a valid scheduler token.

    This decorator is intended to be used on API view methods that should only be accessible by
    scheduled tasks (e.g., cron jobs), not by regular users.
    It checks for a specific token in the request headers and allows the request to proceed if the token matches
    the expected value set in the environment variable `SCHEDULER_TOKEN`.
    If the token is missing or invalid, it returns a JSON response indicating permission denial.
    """

    def __init__(self, func):
        """Initialize the decorator with the function to be wrapped."""
        self.func = func

    def __get__(self, obj, obj_type):
        """Allow the decorator to be used as a method of a class."""
        return functools.partial(self.__call__, obj)

    def __call__(self, *args, **kwargs):
        """Call the wrapped function if the token is valid, otherwise return an error response.

        Args:
            *args: Positional arguments passed to the wrapped function.
            **kwargs: Keyword arguments passed to the wrapped function.

        Returns:
            The result of the decorated function if the token is valid,
            or a JSON response indicating permission denial if the token is invalid or missing.
        """
        self.request = args[1]
        if self.check_token():
            return self.func(*args, **kwargs)
        else:
            return self.error("Permission denied")

    def check_token(self):
        """Check if the request contains a valid scheduler token.

        Returns:
            bool: True if the token is valid, False otherwise.
        """
        expected_token = os.getenv("SCHEDULER_TOKEN", "")
        if not expected_token:
            return False
        received_token = self.request.headers.get("X-Scheduler-Token", "")
        return received_token == expected_token

    def error(self, data):
        """Return a JSON response indicating permission denial."""
        return JSONResponse.response({
            "error": "permission-denied",
            "data": "Scheduler token is invalid or missing",
        })


def scheduler_only(view_func):
    """Function decorator to restrict API access to scheduler-authenticated requests.

    This decorator wraps the given view function and applies the `SchedulerOnlyDecorator`
    to ensure that only requests with a valid scheduler token can access the view.

    Args:
        view_func (callable): The view function to be decorated.

    Returns:
        callable: The wrapped view function.
    """

    @functools.wraps(view_func)
    def wrapped_view(*args, **kwargs):
        decorator = SchedulerOnlyDecorator(view_func)
        return decorator(*args, **kwargs)

    return wrapped_view
