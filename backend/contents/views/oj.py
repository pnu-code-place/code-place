from contents.serializers import HomeStatistics
from contest.models import Contest
from problem.models import Problem
from utils.api import APIView
from django.utils.timezone import now


class GetHomeStatisticsAPI(APIView):
    def get(self, request):
        """
        총 문제 수, 채점이 완료된 문제 수, 마감된 대회 수를 반환하는 API
        """
        problems = Problem.objects.all().filter(visible=True)

        # 총 문제 수
        total_problem_length = problems.count()

        # 한번이라도 accept가 된 문제 수
        accepted_problem_length = problems.filter(accepted_number__lt=0).count()

        # 마감된 대회 수
        contests = Contest.objects.select_related("created_by").filter(visible=True)
        cur = now()
        contests = contests.filter(end_time__lt=cur)
        ended_contest_length = contests.count()

        home_statistics = {
            "total_problem_length": total_problem_length,
            "accepted_problem_length": accepted_problem_length,
            "ended_contest_length": ended_contest_length,
        }

        return self.success(HomeStatistics(home_statistics).data)