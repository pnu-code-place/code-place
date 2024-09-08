import io

import xlsxwriter
from django.db.models import OuterRef, Count, Subquery, F, Max
from django.http import HttpResponse
from django.utils.timezone import now
from django.core.cache import cache

from problem.models import Problem
from submission.models import Submission
from utils.api import APIView, validate_serializer
from utils.constants import CacheKey, CONTEST_PASSWORD_SESSION_KEY
from utils.shortcuts import datetime2str, check_is_id
from account.models import AdminType, User, UserProfile
from account.decorators import login_required, check_contest_permission, check_contest_password

from utils.constants import ContestRuleType, ContestStatus
from ..models import ContestAnnouncement, Contest, OIContestRank, ACMContestRank
from ..serializers import ContestAnnouncementSerializer, ContestUserSubmissionSummarySerializer
from ..serializers import ContestSerializer, ContestPasswordVerifySerializer
from ..serializers import OIContestRankSerializer, ACMContestRankSerializer


class ContestAnnouncementListAPI(APIView):
    @check_contest_permission(check_type="announcements")
    def get(self, request):
        contest_id = request.GET.get("contest_id")
        if not contest_id:
            return self.error("Invalid parameter, contest_id is required")
        data = ContestAnnouncement.objects.select_related("created_by").filter(contest_id=contest_id, visible=True)
        max_id = request.GET.get("max_id")
        if max_id:
            data = data.filter(id__gt=max_id)
        return self.success(ContestAnnouncementSerializer(data, many=True).data)


class ContestAPI(APIView):
    def get(self, request):
        id = request.GET.get("id")
        if not id or not check_is_id(id):
            return self.error("Invalid parameter, id is required")
        try:
            contest = Contest.objects.get(id=id, visible=True)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        data = ContestSerializer(contest).data
        data["now"] = datetime2str(now())
        return self.success(data)


class ContestListAPI(APIView):
    def get(self, request):
        contests = Contest.objects.select_related("created_by").filter(visible=True)
        keyword = request.GET.get("keyword")
        rule_type = request.GET.get("rule_type")
        status = request.GET.get("status")
        if keyword:
            contests = contests.filter(title__contains=keyword)
        if rule_type:
            contests = contests.filter(rule_type=rule_type)
        if status:
            cur = now()
            if status == ContestStatus.CONTEST_NOT_START:
                contests = contests.filter(start_time__gt=cur)
            elif status == ContestStatus.CONTEST_ENDED:
                contests = contests.filter(end_time__lt=cur)
            else:
                contests = contests.filter(start_time__lte=cur, end_time__gte=cur)
        return self.success(self.paginate_data(request, contests, ContestSerializer))

class ContestNotStartedListAPI(APIView):
    def get(self, request):
        contests = Contest.objects.select_related("created_by").filter(visible=True)
        cur = now()
        contests = contests.filter(start_time__gt=cur)
        return self.success(ContestSerializer(contests, many=True).data)

class ContestUnderWayListAPI(APIView):
    def get(self, request):
        contests = Contest.objects.select_related("created_by").filter(visible=True)
        keyword = request.GET.get("keyword")
        rule_type = request.GET.get("rule_type")
        if keyword:
            contests = contests.filter(title__contains=keyword)
        if rule_type:
            contests = contests.filter(rule_type=rule_type)
        cur = now()
        contests = contests.filter(start_time__lte=cur, end_time__gte=cur)
        return self.success(ContestSerializer(contests, many=True).data)

class ContestHistoryListAPI(APIView):
    def get(self, request):
        cur = now()
        contests = Contest.objects.select_related("created_by").filter(visible=True, end_time__lte=cur)
        keyword = request.GET.get("keyword")
        rule_type = request.GET.get("rule_type")
        year = request.GET.get("year")
        month = request.GET.get("month")
        if keyword:
            contests = contests.filter(title__contains=keyword)
        if rule_type:
            contests = contests.filter(rule_type=rule_type)
        if year:
            contests = contests.filter(start_time__year=year)
        if month:
            contests = contests.filter(start_time__month=month)
        return self.success(self.paginate_data(request, contests, ContestSerializer))


class ContestPasswordVerifyAPI(APIView):
    @validate_serializer(ContestPasswordVerifySerializer)
    @login_required
    def post(self, request):
        data = request.data
        try:
            contest = Contest.objects.get(id=data["contest_id"], visible=True, password__isnull=False)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        if not check_contest_password(data["password"], contest.password):
            return self.error("Wrong password or password expired")

        # password verify OK.
        if CONTEST_PASSWORD_SESSION_KEY not in request.session:
            request.session[CONTEST_PASSWORD_SESSION_KEY] = {}
        request.session[CONTEST_PASSWORD_SESSION_KEY][contest.id] = data["password"]
        # https://docs.djangoproject.com/en/dev/topics/http/sessions/#when-sessions-are-saved
        request.session.modified = True
        return self.success(True)


class ContestAccessAPI(APIView):
    @login_required
    def get(self, request):
        contest_id = request.GET.get("contest_id")
        if not contest_id:
            return self.error()
        try:
            contest = Contest.objects.get(id=contest_id, visible=True, password__isnull=False)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        session_pass = request.session.get(CONTEST_PASSWORD_SESSION_KEY, {}).get(contest.id)
        return self.success({"access": check_contest_password(session_pass, contest.password)})


class ContestParticipantsAPI(APIView):
    @login_required
    def get(self, request):
        contest_id = request.GET.get("contest_id")

        submissions = Submission.objects.filter(contest_id=contest_id)

        user_submissions = submissions.values('user_id', 'username').annotate(
            submission_count=Count('id'),
            last_submission_ip=Max('ip')
        ).order_by('user_id')

        # UserProfile 정보 가져오기
        user_profiles = UserProfile.objects.filter(user_id__in=[sub['user_id'] for sub in user_submissions])
        user_profile_dict = {profile.user_id: profile for profile in user_profiles}

        # User 정보 가져오기
        users = User.objects.filter(id__in=[sub['user_id'] for sub in user_submissions])
        user_dict = {user.id: user for user in users}

        result = []
        for submission in user_submissions:
            user = user_dict.get(submission['user_id'])
            profile = user_profile_dict.get(submission['user_id'])
            result.append({
                'user_id': submission['user_id'],
                'username': submission['username'],
                'email': user.email if user else None,
                'avatar': profile.avatar if profile else None,
                'school': profile.school if profile else None,
                'major': profile.major if profile else None,
                'submission_count': submission['submission_count'],
                'last_submission_ip': submission['last_submission_ip']
            })

        serializer = ContestUserSubmissionSummarySerializer(result, many=True)
        return self.success(serializer.data)


class ContestRankAPI(APIView):
    def get_rank(self):
        if self.contest.rule_type == ContestRuleType.ACM:
            return ACMContestRank.objects.filter(contest=self.contest,
                                                 user__admin_type=AdminType.REGULAR_USER,
                                                 user__is_disabled=False).\
                select_related("user").order_by("-accepted_number", "total_time")
        else:
            return OIContestRank.objects.filter(contest=self.contest,
                                                user__admin_type=AdminType.REGULAR_USER,
                                                user__is_disabled=False). \
                select_related("user").order_by("-total_score")

    def column_string(self, n):
        string = ""
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            string = chr(65 + remainder) + string
        return string

    @check_contest_permission(check_type="ranks")
    def get(self, request):
        download_csv = request.GET.get("download_csv")
        force_refresh = request.GET.get("force_refresh")
        is_contest_admin = request.user.is_authenticated and request.user.is_contest_admin(self.contest)
        if self.contest.rule_type == ContestRuleType.OI:
            serializer = OIContestRankSerializer
        else:
            serializer = ACMContestRankSerializer

        if force_refresh == "1" and is_contest_admin:
            qs = self.get_rank()
        else:
            cache_key = f"{CacheKey.contest_rank_cache}:{self.contest.id}"
            qs = cache.get(cache_key)
            if not qs:
                qs = self.get_rank()
                cache.set(cache_key, qs)

        def convert_ms_to_time(ms):
            # 밀리초를 초 단위로 변환
            seconds = ms // 1000

            # 시간 계산
            hours = seconds // 3600
            seconds %= 3600

            # 분 계산
            minutes = seconds // 60
            seconds %= 60

            return f"{hours}시간 {minutes}분 {seconds}초"

        if download_csv:
            data = serializer(qs, many=True, is_contest_admin=is_contest_admin).data
            contest_problems = Problem.objects.filter(contest=self.contest, visible=True).order_by("_id")
            problem_ids = [item.id for item in contest_problems]

            f = io.BytesIO()

            workbook = xlsxwriter.Workbook(f)
            worksheet = workbook.add_worksheet()

            # write contest info
            contest_title = workbook.add_format({'font_size': 30, 'bold': True})
            worksheet.write("A1", self.contest.title, contest_title)
            contest_type = workbook.add_format({'font_size': 15, 'bold': True})
            worksheet.write("A2", "OI 타입" if self.contest.rule_type == ContestRuleType.OI else "ACM 타입", contest_type)
            contest_other_info = workbook.add_format({'bold': True})
            worksheet.write("A3", "대회 시작 시간", contest_other_info)
            worksheet.write("B3", str(self.contest.start_time), contest_other_info)
            worksheet.write("A4", "대회 종료 시간", contest_other_info)
            worksheet.write("B4", str(self.contest.end_time), contest_other_info)

            ranking_bg = workbook.add_format({'bg_color': '#EEECE2', 'bold':True})
            user_info_bg = workbook.add_format({'bg_color': '#DAE4C0', 'bold':True})
            worksheet.write("A6", "순위", ranking_bg)
            worksheet.write("B6", "닉네임", user_info_bg)
            worksheet.write("C6", "실명", user_info_bg)
            worksheet.write("D6", "이메일", user_info_bg)
            worksheet.write("E6", "단과대학", user_info_bg)
            worksheet.write("F6", "학과명", user_info_bg)
            worksheet.write("G6", "학번", user_info_bg)
            if self.contest.rule_type == ContestRuleType.OI:
                total_score_bg = workbook.add_format({'bg_color': '#F6D7B8', 'bold': True})
                worksheet.write("H6", "총점", total_score_bg)
                for item in range(contest_problems.count()):
                    problems_bg = workbook.add_format({'bg_color': '#DEEDF2', 'bold': True})
                    worksheet.write(self.column_string(10 + item) + "6", f"문제 {contest_problems[item]._id}번", problems_bg)
                for index, item in enumerate(data):
                    worksheet.write_string(index + 6, 0, str(index + 1))
                    worksheet.write_string(index + 6, 1, item["user"]["username"])
                    worksheet.write_string(index + 6, 2, item["user"]["real_name"] or "")
                    worksheet.write_string(index + 6, 3, item["user"]["email"] or "")
                    worksheet.write_string(index + 6, 4, item["user"]["school"] or "")
                    worksheet.write_string(index + 6, 5, item["user"]["major"] or "")
                    worksheet.write_string(index + 6, 6, item["user"]["student_id"] or "")
                    worksheet.write_string(index + 6, 7, str(item["total_score"])+ '점')
                    for k, v in item["submission_info"].items():
                        worksheet.write_string(index + 6, 9 + problem_ids.index(int(k)), str(v) + '점' )

            else:
                score_bg = workbook.add_format({'bg_color': '#F6D7B8', 'bold':True})
                worksheet.write("H6", "AC", score_bg)
                worksheet.write("I6", "총 제출 수", score_bg)
                worksheet.write("J6", "총 시간", score_bg)
                for item in range(contest_problems.count()):
                    problems_bg = workbook.add_format({'bg_color': '#DEEDF2', 'bold':True})
                    worksheet.write(self.column_string(12 + item) + "6", f"문제 {contest_problems[item]._id}번", problems_bg)

                for index, item in enumerate(data):
                    worksheet.write_string(index + 6, 0, str(str(index + 1)))
                    worksheet.write_string(index + 6, 1, item["user"]["username"])
                    worksheet.write_string(index + 6, 2, item["user"]["real_name"] or "")
                    worksheet.write_string(index + 6, 3, item["user"]["email"] or "")
                    worksheet.write_string(index + 6, 4, item["user"]["school"] or "")
                    worksheet.write_string(index + 6, 5, item["user"]["major"] or "")
                    worksheet.write_string(index + 6, 6, item["user"]["student_id"] or "")
                    worksheet.write_string(index + 6, 7, str(item["accepted_number"]) + '번')
                    worksheet.write_string(index + 6, 8, str(item["submission_number"]) + '번')
                    worksheet.write_string(index + 6, 9, convert_ms_to_time(item["total_time"]))
                    for k, v in item["submission_info"].items():
                        worksheet.write_string(index + 6, 11 + problem_ids.index(int(k)), str(v["is_ac"]))

            workbook.close()
            f.seek(0)
            response = HttpResponse(f.read())
            response["Content-Disposition"] = f"attachment; filename=content-{self.contest.id}-rank.xlsx"
            response["Content-Type"] = "application/xlsx"
            return response

        page_qs = self.paginate_data(request, qs)
        page_qs["results"] = serializer(page_qs["results"], many=True, is_contest_admin=is_contest_admin).data
        return self.success(page_qs)