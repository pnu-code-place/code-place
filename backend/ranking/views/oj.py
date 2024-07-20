from django.db.models import Sum, Count, F
from django.http import HttpResponseNotFound

from account.models import UserScore, User, Department
from ranking.serializers import HomeRankingSerializer, UserRankListSerializer, SurgeUserSerializer
from utils.api import APIView


class HomeRankingAPI(APIView):
    def get(self, request):
        # rank, avatar, tier, total_score, fluctuation
        limit = request.GET.get('limit', 3)
        try:
            ranking = UserScore.objects.all().order_by('-total_score')[:limit]
        except UserScore.DoesNotExist:
            return self.error('no user score table')
        return self.success(HomeRankingSerializer(ranking, many=True).data)


class UserRankAPI(APIView):
    # def get(self, request):
    #     rule_type = request.GET.get("rule")
    #     if rule_type not in ContestRuleType.choices():
    #         rule_type = ContestRuleType.ACM
    #     profiles = UserProfile.objects.filter(user__admin_type=AdminType.REGULAR_USER, user__is_disabled=False) \
    #         .select_related("user")
    #     if rule_type == ContestRuleType.ACM:
    #         profiles = profiles.filter(submission_number__gt=0).order_by("-accepted_number", "submission_number")
    #     else:
    #         profiles = profiles.filter(total_score__gt=0).order_by("-total_score")
    #     return self.success(self.paginate_data(request, profiles, RankInfoSerializer))
    def get(self, request):
        offset = int(request.GET.get("offset", 0))
        limit = int(request.GET.get("limit", 10))

        users = User.objects.prefetch_related('userprofile', 'userscore', 'usersolved') \
                    .order_by('-userscore__total_score')[offset:offset + limit]

        total_users = User.objects.count()

        results = []
        for rank, user in enumerate(users, start=offset + 1):
            serializer = UserRankListSerializer(user, context={'rank': rank})
            results.append(serializer.data)

        data = {
            'total': total_users,
            'results': results
        }

        return self.success(data)


class SurgeUserRankAPI(APIView):
    def get(self, request):
        offset = int(request.GET.get("offset", 0))
        limit = int(request.GET.get("limit", 10))

        users = User.objects.prefetch_related('userprofile', 'userscore', 'usersolved') \
                    .order_by('-userscore__fluctuation')[offset:offset + limit]

        total_users = User.objects.count()

        results = []
        for rank, user in enumerate(users, start=offset + 1):
            serializer = SurgeUserSerializer(user, context={'rank': rank})
            results.append(serializer.data)

        data = {
            'total': total_users,
            'results': results
        }

        return self.success(data)


class MajorRankAPI(APIView):
    def get(self, request):
        limit = int(request.GET.get("limit", 7))

        major_ranks = Department.objects.annotate(
            score=Sum('userprofile__user__userscore__total_score'),
            people=Count('userprofile__user')
        ).filter(score__isnull=False).order_by('-score')[:limit]

        total_majors = major_ranks.count()

        results = []
        for rank, major in enumerate(major_ranks, start=1):
            people_data = major.userprofile_set.select_related('user', 'user__userscore').annotate(
                avatar_url=F('user__userprofile__avatar'),
                username=F('user__username'),
                score=F('user__userscore__total_score'),
                tier=F('user__userscore__tier')
            ).order_by('-user__userscore__total_score').values('avatar_url', 'username', 'mood', 'score', 'tier')

            data = {
                'rank': rank,
                'major': major.department_name,
                'score': major.score,
                'people': list(people_data)
            }
            results.append(data)

        data = {
            'total': total_majors,
            'results': results
        }

        return self.success(data)
