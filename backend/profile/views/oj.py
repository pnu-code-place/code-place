import os

from django.db.models import OuterRef, Subquery, Q, Count, F
from django.http import HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from account.decorators import login_required
from account.models import User, UserProfile, UserScore, UserSolved
from oj import settings
from profile.serializers import ProfileProblemSerializer, UserProfileSerializer, EditUserProfileSerializer, \
    DashboardSubmissionSerializer, DashboardRankSerializer, DashboardFieldInfoSerializer, \
    DashboardDifficultyInfoSerializer, ImageUploadForm
from school.models import Department, College
from submission.models import Submission
from utils.api import APIView, validate_serializer
from utils.constants import ProblemField
from utils.shortcuts import rand_str


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
                datastructure_rank=Count('datastructure_score',
                                         filter=Q(datastructure_score__gt=F('datastructure_score'))) + 1,
                implementation_rank=Count('implementation_score',
                                          filter=Q(implementation_score__gt=F('implementation_score'))) + 1,
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
        username = request.GET.get('username')
        if not username:
            self.error("username is required")

        field = request.GET.get('field')
        difficulty = request.GET.get('difficulty')
        status = request.GET.get('status')

        user_id = User.objects.get(username=username).id

        # 각 문제별 최신 제출을 찾는 서브쿼리
        latest_submissions = Submission.objects.filter(
            user_id=user_id, problem=OuterRef('problem')).order_by('-create_time').values('id')[:1]

        # 메인 쿼리
        submissions = Submission.objects.filter(
            id__in=Subquery(latest_submissions)).select_related('problem').order_by('-create_time')

        if field and field != 'All':
            submissions = submissions.filter(problem__field=field)
        if difficulty and difficulty != 'All':
            submissions = submissions.filter(problem__difficulty=difficulty)
        if status and status != 'All':
            if status == "Solved":
                submissions = submissions.filter(result=0)
            else:
                submissions = submissions.filter(~Q(result=0))

        result = []
        for submission in submissions:
            result.append({
                'id': submission.problem._id,
                'title': submission.problem.title,
                'submitTime': submission.create_time,
                'difficulty': submission.problem.difficulty,
                'field': ProblemField.intToStr[submission.problem.field],
            })

        serializer = ProfileProblemSerializer(data=result, many=True)
        serializer.is_valid(raise_exception=True)
        return self.success(serializer.data)
