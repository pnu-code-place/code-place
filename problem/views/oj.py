import random
from django.db.models import Q, Count
from utils.api import APIView
from account.decorators import check_contest_permission, login_required
from ..models import ProblemTag, Problem, ProblemRuleType
from ..serializers import ProblemSerializer, TagSerializer, ProblemSafeSerializer, RecommendBonusProblemSerializer,MostDifficultProblemSerializer
from contest.models import ContestRuleType
from account.models import UserProfile, UserScore
from submission.models import JudgeStatus
from django.http import HttpResponseNotFound, HttpResponseBadRequest
from utils.constants import ProblemField, Difficulty, Tier


class ProblemTagAPI(APIView):
    def get(self, request):
        qs = ProblemTag.objects
        keyword = request.GET.get("keyword")
        if keyword:
            qs = ProblemTag.objects.filter(name__icontains=keyword)
        tags = qs.annotate(problem_count=Count("problem")).filter(problem_count__gt=0)
        return self.success(TagSerializer(tags, many=True).data)


class PickOneAPI(APIView):
    def get(self, request):
        problems = Problem.objects.filter(contest_id__isnull=True, visible=True)
        count = problems.count()
        if count == 0:
            return self.error("No problem to pick")
        return self.success(problems[random.randint(0, count - 1)]._id)


class BonusProblemAPI(APIView):
    def get(self, request):
        bonus_problems = Problem.objects.filter(contest_id__isnull=True, visible=True, is_bonus=True)
        if not bonus_problems:
            return HttpResponseNotFound("No bonus problem")
        return self.success(RecommendBonusProblemSerializer(bonus_problems, many=True).data)


class ProblemAPI(APIView):
    @staticmethod
    def _add_problem_status(request, queryset_values):
        if request.user.is_authenticated:
            profile = request.user.userprofile
            acm_problems_status = profile.acm_problems_status.get("problems", {})
            oi_problems_status = profile.oi_problems_status.get("problems", {})
            # paginate data
            results = queryset_values.get("results")
            if results is not None:
                problems = results
            else:
                problems = [queryset_values, ]
            for problem in problems:
                if problem["rule_type"] == ProblemRuleType.ACM:
                    problem["my_status"] = acm_problems_status.get(str(problem["id"]), {}).get("status")
                else:
                    problem["my_status"] = oi_problems_status.get(str(problem["id"]), {}).get("status")

    def get(self, request):
        # 问题详情页
        problem_id = request.GET.get("problem_id")
        if problem_id:
            try:
                problem = Problem.objects.select_related("created_by") \
                    .get(_id=problem_id, contest_id__isnull=True, visible=True)
                problem_data = ProblemSerializer(problem).data
                self._add_problem_status(request, problem_data)
                return self.success(problem_data)
            except Problem.DoesNotExist:
                return self.error("Problem does not exist")

        limit = request.GET.get("limit")
        if not limit:
            return self.error("Limit is needed")

        problems = Problem.objects.select_related("created_by").filter(contest_id__isnull=True, visible=True)
        # 按照标签筛选
        tag_text = request.GET.get("tag")
        if tag_text:
            problems = problems.filter(tags__name=tag_text)

        # 搜索的情况
        keyword = request.GET.get("keyword", "").strip()
        if keyword:
            problems = problems.filter(Q(title__icontains=keyword) | Q(_id__icontains=keyword))

        # 难度筛选
        difficulty = request.GET.get("difficulty")
        if difficulty:
            problems = problems.filter(difficulty=difficulty)

        field = request.GET.get("field")
        if field:
            problems = problems.filter(field=field)

        # 根据profile 为做过的题目添加标记
        data = self.paginate_data(request, problems, ProblemSerializer)
        self._add_problem_status(request, data)
        return self.success(data)


class ContestProblemAPI(APIView):
    def _add_problem_status(self, request, queryset_values):
        if request.user.is_authenticated:
            profile = request.user.userprofile
            if self.contest.rule_type == ContestRuleType.ACM:
                problems_status = profile.acm_problems_status.get("contest_problems", {})
            else:
                problems_status = profile.oi_problems_status.get("contest_problems", {})
            for problem in queryset_values:
                problem["my_status"] = problems_status.get(str(problem["id"]), {}).get("status")

    @check_contest_permission(check_type="problems")
    def get(self, request):
        problem_id = request.GET.get("problem_id")
        if problem_id:
            try:
                problem = Problem.objects.select_related("created_by").get(_id=problem_id,
                                                                           contest=self.contest,
                                                                           visible=True)
            except Problem.DoesNotExist:
                return self.error("Problem does not exist.")
            if self.contest.problem_details_permission(request.user):
                problem_data = ProblemSerializer(problem).data
                self._add_problem_status(request, [problem_data, ])
            else:
                problem_data = ProblemSafeSerializer(problem).data
            return self.success(problem_data)

        contest_problems = Problem.objects.select_related("created_by").filter(contest=self.contest, visible=True)
        if self.contest.problem_details_permission(request.user):
            data = ProblemSerializer(contest_problems, many=True).data
            self._add_problem_status(request, data)
        else:
            data = ProblemSafeSerializer(contest_problems, many=True).data
        return self.success(data)


class RecommendProblemAPI(APIView):
    @login_required
    def get(self, request):
        """사용자의 실력에 맞는 3문제를 추천합니다.

        추천 문제는 사용자의 현재 점수에 맞는 난이도를 가져야 합니다.
        가장 약한 분야부터 시작하여, 3문제가 추천됩니다.

        OK(200):
            - 다섯 분야의 사용자 점수와 추천된 세 문제가 반환됩니다.

        BadRequest(400):
            - 사용자가 푼 문제가 10개 미만인 경우, 추천을 받기에 데이터가 충분하지 않습니다.
            - 추천할 문제가 0개인 경우입니다. CSEP의 총 문제 개수가 충분하지 않을 때 발생할 수 있습니다.

        NotFound(404):
            - 요청한 사용자의 UserScore 또는 UserProfile이 존재하지 않습니다.
        """
        # user_score = self.get_user_score(request.user)
        # user_solved_problems = self.get_user_solved_problems(request.user)
        #
        # if len(user_solved_problems) < 10:
        #     return HttpResponseBadRequest('User should solve at least 10 problems.')
        #
        # field_scores = self.get_field_scores(user_score)
        # difficulty = self.get_recommend_difficulty(user_score)
        # recommend_problems = self.get_recommend_problems(field_scores, difficulty, user_solved_problems)
        #
        # if recommend_problems:
        #     return self.success({
        #         "field_score": field_scores,
        #         "recommend_problems": RecommendBonusProblemSerializer(recommend_problems, many=True).data})
        # else:
        #     return HttpResponseBadRequest("No Recommendation because of insufficient problems.")
        user_score = self.get_user_score(request.user)
        user_solved_problem = self.get_user_solved_problems(request.user)
        field_scores = self.get_field_scores(user_score)

        difficulty = self.get_recommend_difficulty(user_score)
        candidate_problems = Problem.objects.filter(
            difficulty__in=difficulty, visible=True, contest__isnull=True).exclude(_id__in=user_solved_problem)
        recommend_problems = random.sample(list(candidate_problems), min(3, len(candidate_problems)))

        if recommend_problems:
            return self.success({
                'field_score': field_scores,
                'recommend_problems': RecommendBonusProblemSerializer(recommend_problems, many=True).data
            })
        else:
            return HttpResponseBadRequest("No recommendation because of insufficient problems.")

    @staticmethod
    def get_user_score(user):
        """사용자의 UserScore ORM Model을 반환합니다."""
        try:
            return UserScore.objects.get(user=user)
        except UserScore.DoesNotExist:
            return HttpResponseNotFound("UserScore does not exist.")

    @staticmethod
    def get_user_solved_problems(user):
        """사용자가 이미 푼 문제들의 id를 List로 반환합니다."""
        try:
            solved_problems = UserProfile.objects.get(user=user).acm_problems_status.get("problems", {})
        except UserProfile.DoesNotExist:
            return HttpResponseNotFound("UserProfile does not exist.")
        return [v['_id'] for k, v in solved_problems.items() if v['status'] == JudgeStatus.ACCEPTED]

    @staticmethod
    def get_recommend_difficulty(user_score):
        """사용자의 총 점수를 토대로 적절한 난이도를 반환합니다.

        총 점수에 따른 추천 난이도는 다음과 같습니다.
            - sprout ~ silver1: [VeryLow, Low]
            - gold3 ~ gold1: [Mid]
            - platinum3 ~ diamond1: [High, VeryHigh]
        """
        if 0 <= user_score.total_score <= Tier.tiers['silver1']:
            return [Difficulty.VERYLOW, Difficulty.LOW]
        elif Tier.tiers['gold3'] <= user_score.total_score <= Tier.tiers['gold1']:
            return [Difficulty.MID]
        else:
            return [Difficulty.HIGH, Difficulty.VERYHIGH]

    @staticmethod
    def get_field_scores(user_score):
        """각 영역의 이름과 점수 리스트를 점수에 따른 오름차순으로 정렬 후 반환합니다."""
        field_scores = [{'name': field_name, 'score': getattr(user_score, field_name + '_score')}
                        for field_name in ProblemField.fields]
        field_scores.sort(key=lambda x: x['score'])
        return field_scores

    @staticmethod
    def get_recommend_problems(field_scores, difficulty, user_solved_problems):
        """추천 문제를 반환합니다.

        Args:
            field_scores(List[Dict['name', 'score']): 사용자의 모든 영역에 대한 [영역이름, 점수] List, 점수로 오름차순 정렬
            difficulty(String): 추천할 문제의 난이도
            user_solved_problems(List[String]): 사용자가 이미 푼 문제의 display_id List
        """
        recommend_problems = []
        for field_score in field_scores:
            # 문제의 영역 컬럼은 정수이기 때문에 필드의 idx를 가져옵니다.
            field_idx = ProblemField.strToInt[field_score['name']]
            candidate_problems = Problem.objects.filter(
                field=field_idx, difficulty__in=difficulty, visible=True, contest__isnull=True) \
                .exclude(_id__in=user_solved_problems)
            # 추천문제가 총 3개가 되도록 문제를 선택합니다.
            num_to_pick = min(3 - len(recommend_problems), len(candidate_problems))
            # 후보 문제 중 랜덤으로 recommend_problems에 추가합니다.
            recommend_problems.extend(random.sample(list(candidate_problems), num_to_pick))
            if len(recommend_problems) == 3:
                break
        return recommend_problems

class MostDifficultProblemAPI(APIView):
    def get(self, request):
        most_difficult_problem = Problem.objects.filter(is_most_difficult=True, visible=True).first()
        if not most_difficult_problem:
            return HttpResponseNotFound("There is No most difficult problem in last week")
        serializer = MostDifficultProblemSerializer(most_difficult_problem)
        return self.success(serializer.data)
