from django.db.models import OuterRef, Subquery, Q

from profile.serializers import ProfileProblemSerializer
from submission.models import Submission
from utils.api import APIView
from utils.constants import ProblemField


class ProfileProblemAPIView(APIView):

    def get(self, request):
        username = request.GET.get('username')
        if not username:
            self.error("username is required")

        field = request.GET.get('field') # Problem 모델에서 검색
        difficulty = request.GET.get('difficulty') # Problem 모델에서 검색
        status = request.GET.get('status') # Submission 모델에서 result가 0이면 Solved 상태

        # 각 문제별 최신 제출을 찾는 서브쿼리
        latest_submissions = Submission.objects.filter(
            username=username,
            problem=OuterRef('problem')
        ).order_by('-create_time').values('id')[:1]

        # 메인 쿼리
        submissions = Submission.objects.filter(
            id__in=Subquery(latest_submissions)
        ).select_related('problem').order_by('-create_time')

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





