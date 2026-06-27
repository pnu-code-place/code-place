import os
import datetime

from django.db.models import Q, Count, F
from django.http import HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from account.decorators import login_required
from account.models import User, UserProfile, UserScore, UserSolved
from oj import settings
from profile.serializers import ProfileProblemSerializer, UserProfileSerializer, EditUserProfileSerializer, \
    DashboardSubmissionSerializer, DashboardRankSerializer, DashboardFieldInfoSerializer, \
    DashboardDifficultyInfoSerializer, ImageUploadForm
from school.models import Department, College
from submission.models import JudgeStatus, Submission
from utils.api import APIView, validate_serializer
from utils.constants import ProblemField
from utils.shortcuts import rand_str


DEFAULT_ACTIVITY_DAYS = 365
MAX_ACTIVITY_DAYS = 366
ACTIVITY_DAY_START_HOUR = 6
ACTIVITY_DAY_BOUNDARY = "6:00 UTC+9"


def get_activity_service_date(dt, current_timezone):
    local_dt = timezone.localtime(dt, current_timezone)
    return (local_dt - datetime.timedelta(hours=ACTIVITY_DAY_START_HOUR)).date()


def get_activity_day_bounds(days, current_timezone):
    end_date = (timezone.localtime(timezone.now(), current_timezone) -
                datetime.timedelta(hours=ACTIVITY_DAY_START_HOUR)).date()
    start_date = end_date - datetime.timedelta(days=days - 1)
    start_datetime = timezone.make_aware(
        datetime.datetime.combine(start_date, datetime.time(hour=ACTIVITY_DAY_START_HOUR)),
        current_timezone,
    )
    end_datetime = timezone.make_aware(
        datetime.datetime.combine(end_date + datetime.timedelta(days=1),
                                  datetime.time(hour=ACTIVITY_DAY_START_HOUR)),
        current_timezone,
    )
    return start_date, end_date, start_datetime, end_datetime


def calculate_activity_streaks(start_date, end_date, count_by_date):
    current_streak = 0
    current_date = end_date
    while current_date >= start_date and count_by_date.get(current_date, 0) > 0:
        current_streak += 1
        current_date -= datetime.timedelta(days=1)

    longest_streak = 0
    running_streak = 0
    current_date = start_date
    while current_date <= end_date:
        if count_by_date.get(current_date, 0) > 0:
            running_streak += 1
            longest_streak = max(longest_streak, running_streak)
        else:
            running_streak = 0
        current_date += datetime.timedelta(days=1)

    return current_streak, longest_streak


class UserProfileAPI(APIView):

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, **kwargs):
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
                show_real_name = True
        except User.DoesNotExist:
            return self.error("User does not exist")
        return self.success(UserProfileSerializer(user.userprofile, show_real_name=show_real_name).data)

    @validate_serializer(EditUserProfileSerializer)
    @login_required
    def put(self, request):
        data = request.data
        if data["username"]:
            user = User.objects.get(username=request.user.username)
            user.username = data["username"]
            user.save()
            request.user.username = data["username"]
        user_profile = request.user.userprofile
        for k, v in data.items():
            if k == "college" and v is not None:
                college = College.objects.get(id=data["college"])
                setattr(user_profile, k, college)
                setattr(user_profile, "school", college.college_name)
                continue
            if k == "department" and v is not None:
                department = Department.objects.get(id=data["department"])
                setattr(user_profile, k, department)
                setattr(user_profile, "major", department.department_name)
                continue
            setattr(user_profile, k, v)
        user_profile.save()
        return self.success(UserProfileSerializer(user_profile, show_real_name=True).data)


class UserProfileDashBoardAPI(APIView):

    @login_required
    def get(self, request):
        try:
            username = request.GET.get("username")
            user_profile = UserProfile.objects.filter(user__username=username).first()
            user_id = user_profile.user_id
            user_score = UserScore.objects.filter(user_id=user_id).annotate(
                total_rank=Count('total_score', filter=Q(total_score__gt=F('total_score'))) + 1,
                datastructure_rank=Count(
                    'datastructure_score', filter=Q(datastructure_score__gt=F('datastructure_score'))) + 1,
                implementation_rank=Count(
                    'implementation_score', filter=Q(implementation_score__gt=F('implementation_score'))) + 1,
                math_rank=Count('math_score', filter=Q(math_score__gt=F('math_score'))) + 1,
                search_rank=Count('search_score', filter=Q(search_score__gt=F('search_score'))) + 1,
                sorting_rank=Count('sorting_score', filter=Q(sorting_score__gt=F('sorting_score'))) + 1,
                algorithm_rank=Count('algorithm_score', filter=Q(algorithm_score__gt=F('algorithm_score'))) +
                1).first()
            user_solved = UserSolved.objects.filter(user_id=user_id).first()
        except User.DoesNotExist or UserProfile.DoesNotExist:
            return HttpResponseNotFound('user does not exist')
        except Department.DoesNotExist or College.DoesNotExist:
            return HttpResponseNotFound('department or college does not exist')
        except UserScore.DoesNotExist:
            return HttpResponseNotFound('user_score does not exist')

        total_user_count = UserScore.objects.filter(user__is_disabled=False).count()
        """ Build oj_status """
        ojStatus = {}
        ojStatus.update(DashboardSubmissionSerializer(user_profile).data)
        ojStatus.update(DashboardRankSerializer(user_score, context={'total_user_count': total_user_count}).data)
        """ Build fieldInfo """
        fieldInfo = DashboardFieldInfoSerializer(user_score).data['fieldInfo']
        """ Build difficultyInfo"""
        difficultyInfo = DashboardDifficultyInfoSerializer(user_solved).data['difficultyInfo']

        response_data = {'ojStatus': ojStatus, 'fieldInfo': fieldInfo, 'difficultyInfo': difficultyInfo}
        return self.success(response_data)


class UserProfileActivityAPI(APIView):

    @login_required
    def get(self, request):
        username = request.GET.get("username")
        if not username:
            return self.error("username is required")

        days_param = request.GET.get("days", DEFAULT_ACTIVITY_DAYS)
        try:
            days = int(days_param)
        except (TypeError, ValueError):
            return self.error("days must be an integer")
        if days < 1 or days > MAX_ACTIVITY_DAYS:
            return self.error(f"days must be between 1 and {MAX_ACTIVITY_DAYS}")

        try:
            user = User.objects.get(username=username, is_disabled=False)
        except User.DoesNotExist:
            return self.error("User does not exist")

        current_timezone = timezone.get_current_timezone()
        start_date, end_date, start_datetime, end_datetime = get_activity_day_bounds(days, current_timezone)

        submissions = (
            Submission.objects
            .filter(
                user_id=user.id,
                result=JudgeStatus.ACCEPTED,
                create_time__gte=start_datetime,
                create_time__lt=end_datetime,
            )
            .order_by("create_time")
            .values_list("create_time", flat=True)
        )
        count_by_date = {}
        for create_time in submissions:
            activity_date = get_activity_service_date(create_time, current_timezone)
            count_by_date[activity_date] = count_by_date.get(activity_date, 0) + 1

        current_streak, longest_streak = calculate_activity_streaks(start_date, end_date, count_by_date)
        activity_days = []
        total_count = 0
        max_count = 0
        for activity_date, count in sorted(count_by_date.items()):
            activity_days.append({"date": activity_date.isoformat(), "count": count})
            total_count += count
            max_count = max(max_count, count)

        return self.success({
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total": total_count,
            "max_count": max_count,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "day_boundary": ACTIVITY_DAY_BOUNDARY,
            "days": activity_days,
        })


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


class ProfileProblemAPIView(APIView):

    def get(self, request):
        """Get submissions of a user.

        This API retrieves submissions of a user and returns the details.
        Submissions can be filtered by various parameters like below.

        Query Parameters:
            username (Optional[str]): Target username
            field (Optional[str]): Problem field
            difficulty (Optional[str]): Problem difficulty
            status (Optional[str]): Submission status
            startDate (Optional[str]): Start date for filtering (YYYY-MM-DD)
            endDate (Optional[str]): End date for filtering (YYYY-MM-DD)
        
        Returns:
            ProfileProblemSerializer.data: List of submissions.
        """
        username = request.GET.get('username')
        if not username:
            return self.error("username is required")

        field = request.GET.get('field')
        difficulty = request.GET.get('difficulty')
        status = request.GET.get('status')
        start_date_str = request.GET.get('startDate')
        end_date_str = request.GET.get('endDate')

        user = User.objects.filter(username=username).first()
        if not user:
            return self.error("User does not exist")

        submissions = Submission.objects.filter(user_id=user.id).select_related('problem').order_by('-create_time')

        # Filtering
        if field and field != 'All':
            if field in ProblemField.strToInt:
                field = ProblemField.strToInt[field]
            else:
                try:
                    field = int(field)
                except (TypeError, ValueError):
                    return self.error("Invalid field")
                if field not in ProblemField.intToStr:
                    return self.error("Invalid field")
            submissions = submissions.filter(problem__field=field)
        if difficulty and difficulty != 'All':
            submissions = submissions.filter(problem__difficulty=difficulty)
        if status and status != 'All':
            if status == "Solved":
                submissions = submissions.filter(result=0)
            elif status == "Failed":
                submissions = submissions.filter(~Q(result=0))
            else:
                return self.error("Invalid status")

        # Date Filtering
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None
        except ValueError:
            return self.error("Invalid date format. Should be YYYY-MM-DD.")

        if start_date and end_date:
            submissions = submissions.filter(
                create_time__gte=start_date, create_time__lt=(end_date + datetime.timedelta(days=1)))
        elif start_date:
            submissions = submissions.filter(create_time__gte=start_date)
        elif end_date:
            submissions = submissions.filter(create_time__lt=(end_date + datetime.timedelta(days=1)))

        result = []
        for submission in submissions:
            result.append({
                'submissionId': submission.id,
                'id': submission.problem._id,
                'title': submission.problem.title,
                'submitTime': submission.create_time,
                'difficulty': submission.problem.difficulty,
                'field': ProblemField.intToStr[submission.problem.field],
                'status': submission.result,
            })

        serializer = ProfileProblemSerializer(data=result, many=True)
        serializer.is_valid(raise_exception=True)
        return self.success(serializer.data)
