import logging
import random
import json

from django.db import transaction
from django.db.models import Case, Count, ExpressionWrapper, F, FloatField, IntegerField, Q, Value, When
from django.http import HttpResponseBadRequest, HttpResponseNotFound, StreamingHttpResponse
from django.contrib.auth import get_user_model
from django.core.cache import cache

from account.decorators import (check_contest_permission, check_contest_password, scheduler_only)
from utils.constants import CONTEST_PASSWORD_SESSION_KEY
from account.models import UserProfile, UserScore
from contest.models import Contest, ContestRuleType, ContestStatus, ContestType
from submission.models import JudgeStatus, Submission
from utils.api import APIView
from utils.constants import Difficulty, HINT_LIMIT_PER_PROBLEM, ProblemField, Tier
from utils.observability_metrics import AI_HINT_API_OUTCOME_TOTAL
from utils.throttling import TokenBucket

from ..ai_assistant import chat_hint, stage_hint
from ..ai_assistant.client import LLMHintError
from ..ai_assistant.messages import AIHintMessage
from ..models import (AIHintMode, Problem, ProblemRuleType, ProblemTag, ProblemAIHintLog)
from ..serializers import (MostDifficultProblemSerializer, ProblemSafeSerializer, ProblemSerializer, ProblemPublicListSerializer,
                           RecommendBonusProblemSerializer, TagSerializer, AIHintLogSerializer)
from ..tasks import update_weekly_stats

logger = logging.getLogger(__name__)


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
        problem = problems[random.randint(0, count - 1)]
        if request.GET.get("summary"):
            return self.success(MostDifficultProblemSerializer(problem).data)
        return self.success(problem._id)


class WeeklyTopProblemsAPI(APIView):

    def get(self, request):
        problems = Problem.objects.filter(
            contest_id__isnull=True,
            visible=True,
        ).values("_id", "title", "difficulty", "field", "curr_week_info")

        sorted_problems = sorted(
            problems,
            key=lambda p: p["curr_week_info"].get("accepted", 0),
            reverse=True,
        )[:3]

        data = [
            {
                "_id": p["_id"],
                "title": p["title"],
                "difficulty": p["difficulty"],
                "field": p["field"],
                "accepted": p["curr_week_info"].get("accepted", 0),
                "submission": p["curr_week_info"].get("submission", 0),
            }
            for p in sorted_problems
        ]
        return self.success(data)


class BonusProblemAPI(APIView):

    def get(self, request):
        bonus_problems = Problem.objects.filter(contest_id__isnull=True, visible=True, is_bonus=True)
        if not bonus_problems:
            return HttpResponseNotFound("No bonus problem")
        return self.success(RecommendBonusProblemSerializer(bonus_problems, many=True).data)


class ProblemAPI(APIView):
    DIFFICULTY_ORDER = {
        Difficulty.VERYLOW: 1,
        Difficulty.LOW: 2,
        Difficulty.MID: 3,
        Difficulty.HIGH: 4,
        Difficulty.VERYHIGH: 5,
    }

    SORT_FIELDS = {
        "id_desc": ("-create_time", "-_id"),
        "id_asc": ("create_time", "_id"),
        "create_time_desc": ("-create_time", "-_id"),
        "create_time_asc": ("create_time", "_id"),
        "difficulty_asc": ("difficulty_order", "_id"),
        "difficulty_desc": ("-difficulty_order", "_id"),
        "accepted_desc": ("-accepted_number", "_id"),
        "accepted_asc": ("accepted_number", "_id"),
        "ac_rate_desc": ("-ac_rate", "_id"),
        "ac_rate_asc": ("ac_rate", "_id"),
    }

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
                problems = [
                    queryset_values,
                ]
            for problem in problems:
                if problem["rule_type"] == ProblemRuleType.ACM:
                    problem["my_status"] = acm_problems_status.get(str(problem["id"]), {}).get("status")
                else:
                    problem["my_status"] = oi_problems_status.get(str(problem["id"]), {}).get("status")

    def get(self, request):
        # 问题详情页
        problem_id = request.GET.get("problem_id")
        # problem_id가 제공되면 문제 상세 정보를 반환합니다.
        if problem_id:
            if not request.user.is_authenticated:
                return self.error("Please login first", err="permission-denied", status=401)
            try:
                problem = Problem.objects.select_related("created_by") \
                    .get(_id=problem_id, contest_id__isnull=True, visible=True)
                problem_data = ProblemSerializer(problem).data
                self._add_problem_status(request, problem_data)
                problem_data["allow_paste"] = True    # 기본 문제는 복사 붙여넣기 허용
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

        sort = request.GET.get("sort")
        if sort in self.SORT_FIELDS:
            problems = problems.annotate(
                difficulty_order=Case(
                    *[
                        When(difficulty=difficulty, then=Value(order))
                        for difficulty, order in self.DIFFICULTY_ORDER.items()
                    ],
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                ac_rate=Case(
                    When(submission_number=0, then=Value(0.0)),
                    default=ExpressionWrapper(
                        F("accepted_number") * 1.0 / F("submission_number"),
                        output_field=FloatField(),
                    ),
                    output_field=FloatField(),
                ),
            ).order_by(*self.SORT_FIELDS[sort])
        else:
            # 문제 기본 정렬: 최신 등록일 내림차순 (동일 일시일 경우 ID 내림차순)
            problems = problems.order_by("-create_time", "-_id")

        # 根据profile 为做过的题目添加标记
        serializer_class = ProblemSerializer if request.user.is_authenticated else ProblemPublicListSerializer
        data = self.paginate_data(request, problems, serializer_class)
        self._add_problem_status(request, data)
        return self.success(data)


# 답변 중 표시 만료 시간
AI_HINT_BUSY_TTL_SEC = 60
# 질문 속도 제한, 토큰 10개, 20초당 1개 충전
AI_HINT_BUCKET = {"capacity": 10, "fill_rate": 1 / 20, "default_capacity": 10}


class ProblemLLMHintAPI(APIView):

    @staticmethod
    def _busy_key(user_id):
        return f"ai_hint:busy:{user_id}"

    def _acquire_busy(self, request, scope):
        """답변 중 표시 남기기, 이미 있으면 거절 응답 반환"""
        key = self._busy_key(request.user.id)
        try:
            acquired = cache.add(key, 1, timeout=AI_HINT_BUSY_TTL_SEC)
        except Exception:
            logger.warning("AI hint busy flag unavailable, continuing without it", exc_info=True)
            return None, None
        if not acquired:
            return None, self._error_response(
                AIHintMessage.BUSY,
                err="ai-hint-busy",
                metric_status="busy",
                scope=scope,
            )
        return key, None

    def _consume_bucket(self, request, scope):
        """질문 토큰 1개 사용, 없으면 거절 응답 반환"""
        bucket = TokenBucket(key=f"ai_hint:bucket:{request.user.id}", redis_conn=cache, **AI_HINT_BUCKET)
        try:
            allowed, wait = bucket.consume()
        except Exception:
            logger.warning("AI hint token bucket unavailable, continuing without it", exc_info=True)
            return None
        if allowed:
            return None
        wait_sec = max(1, int(wait + 0.999))
        return self._error_response(
            AIHintMessage.THROTTLED.format(wait=wait_sec),
            err="ai-hint-throttled",
            metric_status="throttled",
            scope=scope,
            extra={"wait": wait_sec},
        )

    def _release_busy(self, key):
        if not key:
            return
        try:
            cache.delete(key)
        except Exception:
            logger.warning("Failed to release AI hint busy flag %s", key, exc_info=True)

    def _guarded(self, request, scope, handler):
        """답변 중 표시 안에서 handler 실행, 스트리밍 응답이 아니면 표시 삭제"""
        busy_key, error_response = self._acquire_busy(request, scope)
        if error_response:
            return error_response
        # 동시 요청 거절은 토큰을 쓰지 않도록 표시 확인이 먼저
        error_response = self._consume_bucket(request, scope)
        if error_response:
            self._release_busy(busy_key)
            return error_response
        try:
            response = handler(busy_key)
        except Exception:
            self._release_busy(busy_key)
            raise
        if getattr(response, "ai_hint_streaming", False) is not True:
            self._release_busy(busy_key)
        return response

    @staticmethod
    def _format_sse_event(event, data):
        return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    def _streaming_response(self, generator, streaming=False):
        response = StreamingHttpResponse(generator, content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        # 답변 스트림이면 종료 시 표시 삭제
        response.ai_hint_streaming = streaming
        return response

    def _error_events(self, message, err="llm-hint-unavailable", extra=None):
        yield self._format_sse_event("app-error", {"error": err, "message": message, **(extra or {})})
        yield self._format_sse_event("done", {"done": True})

    def _record_outcome(self, status, scope):
        AI_HINT_API_OUTCOME_TOTAL.labels(status=status, scope=scope).inc()

    @staticmethod
    def _persist_hint_log(hint_log, full_text_chunks):
        full_text = "".join(full_text_chunks)
        if full_text.strip():
            if hint_log:
                hint_log.hint_content = full_text
                hint_log.save(update_fields=['hint_content'])
            return True

        if hint_log:
            hint_log.delete()
        return False

    def _error_response(self, message, err="llm-hint-unavailable", metric_status=None, scope="practice", extra=None):
        if metric_status:
            self._record_outcome(metric_status, scope)
        return self._streaming_response(self._error_events(message, err=err, extra=extra))

    def get(self, request):
        scope = "contest" if request.GET.get("contest_id") else "practice"
        if not request.user.is_authenticated:
            return self._error_response(
                AIHintMessage.LOGIN_REQUIRED,
                err="permission-denied",
                metric_status="permission_denied",
                scope=scope,
            )

        return self._guarded(request, scope, lambda busy_key: self._stage_hint(request, scope, busy_key))

    def _stage_hint(self, request, scope, busy_key):
        problem_id = request.GET.get("problem_id")
        contest_id = request.GET.get("contest_id")
        if not problem_id:
            return self._error_response(AIHintMessage.PROBLEM_ID_REQUIRED, metric_status="bad_request", scope=scope)

        # 사용자가 현재 작성 중인 코드 (없으면 None)
        # 서버에서 한 번 더 길이를 제한해 과도하게 큰 요청을 차단
        raw_user_code = request.GET.get("user_code") or ""
        user_code = raw_user_code[:stage_hint.MAX_USER_CODE_LENGTH] if raw_user_code else None
      
        if contest_id:
            try:
                contest = Contest.objects.select_related("created_by").get(id=contest_id, visible=True)
            except Contest.DoesNotExist:
                return self._error_response(
                    AIHintMessage.CONTEST_NOT_FOUND,
                    err="permission-denied",
                    metric_status="permission_denied",
                    scope=scope,
                )

            if not request.user.is_contest_admin(contest):
                if contest.contest_type == ContestType.PASSWORD_PROTECTED_CONTEST:
                    if not check_contest_password(
                        request.session.get(CONTEST_PASSWORD_SESSION_KEY, {}).get(contest.id),
                        contest.password,
                    ):
                        return self._error_response(
                            AIHintMessage.CONTEST_PASSWORD_INVALID,
                            err="permission-denied",
                            metric_status="permission_denied",
                            scope=scope,
                        )

                if contest.status == ContestStatus.CONTEST_NOT_START:
                    return self._error_response(
                        AIHintMessage.CONTEST_NOT_STARTED,
                        err="permission-denied",
                        metric_status="permission_denied",
                        scope=scope,
                    )

            if not contest.ai_assistant_enabled:
                return self._error_response(
                    AIHintMessage.CONTEST_AI_DISABLED,
                    metric_status="disabled",
                    scope=scope,
                )
            try:
                problem = Problem.objects.get(_id=problem_id, contest_id=contest_id, visible=True)
            except Problem.DoesNotExist:
                return self._error_response(AIHintMessage.PROBLEM_NOT_FOUND, metric_status="problem_not_found", scope=scope)
        else:
            try:
                problem = Problem.objects.get(_id=problem_id, contest_id__isnull=True, visible=True)
            except Problem.DoesNotExist:
                return self._error_response(AIHintMessage.PROBLEM_NOT_FOUND, metric_status="problem_not_found", scope=scope)

        hint_log, previous_hints, error_response = self._reserve_hint_log(
            request, problem, scope, mode=AIHintMode.STAGE, code=user_code
        )
        if error_response:
            return error_response

        def make_stream():
            return stage_hint.stream_problem_hint(problem, previous_hints=previous_hints, user_code=user_code)

        return self._streaming_response(
            self._stream_events(make_stream, hint_log, problem_id, scope, AIHintMessage.STAGE_HINT_FAILED, busy_key),
            streaming=True,
        )

    def post(self, request):
        # 일반 문제 자유 질문, 대회 문제는 GET 5단계 힌트 사용
        scope = "practice"
        if not request.user.is_authenticated:
            return self._error_response(
                AIHintMessage.LOGIN_REQUIRED,
                err="permission-denied",
                metric_status="permission_denied",
                scope=scope,
            )

        return self._guarded(request, scope, lambda busy_key: self._chat_hint(request, scope, busy_key))

    def _chat_hint(self, request, scope, busy_key):
        data = request.data or {}
        problem_id = data.get("problem_id")
        if not problem_id:
            return self._error_response(AIHintMessage.PROBLEM_ID_REQUIRED, metric_status="bad_request", scope=scope)

        question = (data.get("question") or "").strip()
        if not question:
            return self._error_response(AIHintMessage.QUESTION_REQUIRED, metric_status="bad_request", scope=scope)
        if len(question) > chat_hint.MAX_QUESTION_LENGTH:
            return self._error_response(
                AIHintMessage.QUESTION_TOO_LONG,
                metric_status="bad_request",
                scope=scope,
            )

        raw_user_code = data.get("code") or ""
        user_code = raw_user_code[:chat_hint.MAX_USER_CODE_LENGTH] if raw_user_code else None
        language = data.get("language") or None

        try:
            problem = Problem.objects.get(_id=problem_id, contest_id__isnull=True, visible=True)
        except Problem.DoesNotExist:
            return self._error_response(AIHintMessage.PROBLEM_NOT_FOUND, metric_status="problem_not_found", scope=scope)

        if language and language not in problem.languages:
            language = None

        # 자유 질문은 횟수 제한 없음
        hint_log, _, error_response = self._reserve_hint_log(
            request, problem, scope, mode=AIHintMode.CHAT, question=question, code=user_code, language=language,
            enforce_limit=False,
        )
        if error_response:
            return error_response

        def make_stream():
            return chat_hint.stream_general_answer(problem, question, user_code=user_code, language=language)

        return self._streaming_response(
            self._stream_events(make_stream, hint_log, problem_id, scope, AIHintMessage.CHAT_ANSWER_FAILED, busy_key),
            streaming=True,
        )

    def _reserve_hint_log(self, request, problem, scope, mode, question=None, code=None, language=None,
                          enforce_limit=True):
        """남은 횟수 확인 후 빈 기록을 먼저 저장해 1회 차감, 기록·이전 힌트 목록·오류 응답 반환"""
        hint_log = None
        previous_hints = []

        if enforce_limit and not (request.user.is_super_admin() or request.user.is_admin()):
            # 트랜잭션을 묶어 체크와 생성이 최대한 원자적으로 이루어지도록 처리
            with transaction.atomic():
                User = get_user_model()
                User.objects.select_for_update().get(pk=request.user.pk)

                # 이전 힌트 로그들 조회 및 시간순 정렬
                previous_logs = ProblemAIHintLog.objects.filter(user=request.user, problem=problem).order_by("created_at")
                problem_hint_count = previous_logs.count()

                if problem_hint_count >= HINT_LIMIT_PER_PROBLEM:
                    return None, [], self._error_response(
                        AIHintMessage.LIMIT_EXCEEDED,
                        err="problem-limit-exceeded",
                        metric_status="problem_limit_exceeded",
                        scope=scope,
                    )

                # 이전 힌트 문자열 추출
                previous_hints = [log.hint_content for log in previous_logs if log.hint_content.strip()]

                # 제한 통과 시, 스트리밍 시작 전에 빈 내용으로 로그를 선제 생성하여 횟수 차감 처리
                hint_log = ProblemAIHintLog.objects.create(
                    user=request.user, problem=problem, hint_content="", mode=mode,
                    student_question=question, student_code=code, student_language=language,
                )
        else:
            # 어드민인 경우에도 이전 힌트 컨텍스트는 유지하도록 조회
            previous_logs = ProblemAIHintLog.objects.filter(user=request.user, problem=problem).order_by("created_at")
            previous_hints = [log.hint_content for log in previous_logs if log.hint_content.strip()]
            hint_log = ProblemAIHintLog.objects.create(
                user=request.user, problem=problem, hint_content="", mode=mode,
                student_question=question, student_code=code, student_language=language,
            )

        return hint_log, previous_hints, None

    def _stream_events(self, make_stream, hint_log, problem_id, scope, error_message, busy_key=None):
        # 호출 준비 중 오류도 SSE 오류 이벤트로 보내기 위해 여기서 호출 시작
        full_text_chunks = []
        try:
            yield from self._stream_events_body(make_stream, hint_log, problem_id, scope, error_message, full_text_chunks)
        finally:
            self._release_busy(busy_key)

    def _stream_events_body(self, make_stream, hint_log, problem_id, scope, error_message, full_text_chunks):
        try:
            for chunk in make_stream():
                full_text_chunks.append(chunk)
                yield self._format_sse_event("chunk", {"text": chunk})
            if self._persist_hint_log(hint_log, full_text_chunks):
                self._record_outcome("success", scope)
            else:
                self._record_outcome("empty_response", scope)
            yield self._format_sse_event("done", {"done": True})
        except LLMHintError as exc:
            logger.warning("Failed to stream LLM hint for problem %s: %s", problem_id, exc)

            self._persist_hint_log(hint_log, full_text_chunks)

            self._record_outcome("llm_error", scope)
            yield from self._error_events(error_message, err="llm-hint-unavailable")

        except (GeneratorExit, BrokenPipeError, ConnectionResetError):
            logger.info("LLM hint stream client disconnected for problem %s", problem_id)

            self._persist_hint_log(hint_log, full_text_chunks)
            self._record_outcome("client_disconnected", scope)
            return

        except Exception:
            logger.exception("Unexpected error while streaming LLM hint for problem %s", problem_id)

            self._persist_hint_log(hint_log, full_text_chunks)

            self._record_outcome("unexpected_error", scope)
            yield from self._error_events(error_message, err="llm-hint-unavailable")


class AIHintHistoryAPI(APIView):

    def get(self, request):
        if not request.user.is_authenticated:
            return self.error("로그인이 필요합니다.")

        problem_id = request.GET.get("problem_id")
        if not problem_id:
            return self.error("problem_id는 필수입니다.")

        # 1. 문제 조회 및 접근 가능 여부(공개 여부, 대회 여부) 검증
        try:
            problem = Problem.objects.get(_id=problem_id, contest_id__isnull=True, visible=True)
        except Problem.DoesNotExist:
            return self.error("문제를 찾을 수 없습니다.")

        # 2. JOIN 없이 Foreign Key를 직접 활용하여 로그 조회
        logs = ProblemAIHintLog.objects.filter(user=request.user, problem=problem).order_by("created_at")

        return self.success({"logs": AIHintLogSerializer(logs, many=True).data})


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
                problem = Problem.objects.select_related("created_by").get(
                    _id=problem_id, contest=self.contest, visible=True)
            except Problem.DoesNotExist:
                return self.error("Problem does not exist.")
            if self.contest.problem_details_permission(request.user):
                problem_data = ProblemSerializer(problem).data
                self._add_problem_status(request, [
                    problem_data,
                ])
            else:
                problem_data = ProblemSafeSerializer(problem).data
            problem_data["allow_paste"] = self.contest.allow_paste    # 대회의 복사 붙여넣기 허용 여부 반환
            return self.success(problem_data)

        contest_problems = Problem.objects.select_related("created_by").filter(contest=self.contest, visible=True)

        query = request.GET.get("query", "").strip()
        if query:
            contest_problems = contest_problems.filter(
                Q(title__icontains=query) | Q(_id__icontains=query) | Q(tags__name__icontains=query)).distinct()

        submission_state_info = {}
        if request.user:
            contest_user_submissions = Submission.objects.filter(
                contest=self.contest, username__exact=request.user.username)
            accepted_submissions = set()
            partially_accepted_submissions = set()
            failed_submissions = set()

            for i in contest_user_submissions.values():
                res = i.get("result")
                problem_id = i["problem_id"]
                if res == JudgeStatus.ACCEPTED:
                    accepted_submissions.add(problem_id)
                elif res == JudgeStatus.PARTIALLY_ACCEPTED:
                    partially_accepted_submissions.add(problem_id)
                else:
                    failed_submissions.add(problem_id)

            submission_state_info = {
                "accepted": accepted_submissions,
                "partially_accepted": partially_accepted_submissions,
                "failed": failed_submissions
            }

        if self.contest.problem_details_permission(request.user):
            data = ProblemSerializer(contest_problems, many=True, context=submission_state_info).data
            self._add_problem_status(request, data)
        else:
            data = ProblemSafeSerializer(contest_problems, many=True, context=submission_state_info).data
        return self.success(data)


class RecommendProblemAPI(APIView):
    # @login_required
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
        if not request.user.is_authenticated:
            return self.success("Not authenticated")
        user_score = self.get_user_score(request.user)
        user_solved_problem = self.get_user_solved_problems(request.user)
        field_scores = self.get_field_scores(user_score)

        # 추천 난이도 임시 제외
        # difficulty = self.get_recommend_difficulty(user_score)
        # candidate_problems = Problem.objects.filter(
        #     difficulty__in=difficulty, visible=True, contest__isnull=True).exclude(_id__in=user_solved_problem)

        candidate_problems = Problem.objects.filter(
            visible=True, contest__isnull=True).exclude(_id__in=user_solved_problem)
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
        field_scores = [{
            'name': field_name,
            'score': getattr(user_score, field_name + '_score')
        } for field_name in ProblemField.fields]
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


class UpdateWeeklyStatsAPI(APIView):

    @scheduler_only
    def post(self, request):
        """Update the weekly statistics of problems.

        Delegates to the `update_weekly_stats` task so that the API and the
        scheduled celery task share the same selection logic.
        """
        try:
            update_weekly_stats()
            return self.success("Weekly stats updated successfully.")
        except Exception as e:
            logging.error("Error updating weekly stats: %s", e)
            return self.error("Failed to update weekly stats.")


class UpdateBonusProblemAPI(APIView):

    DIFFICULTY_GROUPS = [
        [Difficulty.VERYLOW, Difficulty.LOW],
        [Difficulty.MID],
        [Difficulty.HIGH, Difficulty.VERYHIGH],
    ]

    @scheduler_only
    def post(self, request):
        """Update bonus problems by selecting one problem from each difficulty group.

        This method selects one problem from each difficulty group, ensuring that no two problems
        belong to the same field. If no problems are found in a difficulty group, it allows field overlap.
        It updates the selected problems to be marked as bonus problems and resets the bonus status
        for all other problems.
        """
        selected_problem_ids = list()
        selected_fields = set()

        try:
            with transaction.atomic():
                for difficulty in self.DIFFICULTY_GROUPS:
                    candidate_problems = Problem.objects.filter(
                        difficulty__in=difficulty,
                        visible=True,
                        contest__isnull=True,
                    ).exclude(is_bonus=True).exclude(field__in=selected_fields)

                    # If no problems found in the current difficulty group, Allow field overlap
                    if not candidate_problems:
                        candidate_problems = Problem.objects.filter(
                            difficulty__in=difficulty,
                            visible=True,
                            contest__isnull=True,
                        ).exclude(is_bonus=True)

                    # Randomly select one problem from the candidate problems
                    selected_problem = candidate_problems.order_by('?').first()

                    if selected_problem:
                        selected_problem_ids.append(selected_problem.id)
                        selected_fields.add(selected_problem.field)

                Problem.objects.filter(is_bonus=True).update(is_bonus=False)
                Problem.objects.filter(id__in=selected_problem_ids).update(is_bonus=True)
        except Exception as e:
            logging.error("Error updating bonus problems: %s", e)
            return self.error("Failed to update bonus problems.")

        return self.success("Bonus problems updated successfully.")
