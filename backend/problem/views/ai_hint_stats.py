"""AI 조교 사용 현황 집계.

AI 조교는 두 갈래로 동작한다.
- 일반 문제: 자유 질문(`mode=chat`). 횟수 제한 없음
- 대회 문제: 5단계 힌트(`mode=stage`). (사용자, 문제)당 HINT_LIMIT_PER_PROBLEM 회

갈래는 `mode` 가 아니라 **문제가 대회 문제인지(`problem.contest_id`)** 로 나눈다.
`mode` 컬럼은 자유 질문 도입 때 기본값 `stage` 로 추가돼서, 그 전에 일반 문제에서
받은 옛 5단계 힌트도 `stage` 로 남아 있다. `mode` 로 나누면 옛 힌트가 대회 힌트로 섞인다.
일반 문제 안에서만 `mode` 로 자유 질문과 옛 단계 힌트를 구분한다.

집계 범위에 대한 결정
---------------------
**관리자 로그는 제외한다.** 관리자는 횟수 제한을 받지 않아 분포를 왜곡한다.
반대로 `is_disabled` 는 거르지 않는다. 계정이 나중에 비활성화되면 이미 지나간 달의
수치가 소급해서 바뀌기 때문이다. `admin_type` 은 지금 값을 보므로, 학생이 나중에
관리자로 바뀌면 그가 학생일 때 쌓은 기록도 과거 구간에서 사라진다.

**내용이 빈 로그는 제외한다.** 스트리밍 시작 전에 선점 생성되는 행이라
정상 경로에서는 지워지지만, 워커가 중간에 죽으면 그대로 남는다.

**채택률은 일반 문제만 본다.** 대회는 대회마다 AI 조교를 켜고 끄므로 분모가 흔들린다.
분모는 조회 구간 전체라서, AI 조교가 없던 시기까지 포함해 조회하면 실제보다 낮게 나온다.

**학습 효과(정답 도달률) 비교는 넣지 않는다.** 어떤 짝을 모집단에 넣느냐에 따라
결과가 뒤집히고, 무작위 배정이 아니어서 인과로 읽을 수도 없다.
방법론을 먼저 합의한 뒤 별도로 만든다.

**최근 질문은 아이디를 가려서 보낸다.** 학생이 무엇을 묻는지 보려는 목적이라
누가 물었는지는 필요 없다. 가리는 건 서버에서 한다. 화면에서만 가리면 응답에 원본이 남는다.
"""

from datetime import datetime, timedelta

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

from account.decorators import super_admin_required
from account.models import AdminType
from utils.api import APIView
from utils.constants import HINT_LIMIT_PER_PROBLEM

from ..models import AIHintMode

# `submission.create_time` 에 인덱스가 없고, `problem_ai_hint_log` 의 인덱스는 전부
# `user`/`problem` 으로 시작해서 `created_at` 단독 범위 조건으로는 탐색이 안 된다.
# 그래서 조회 구간이 넓으면 양쪽 다 전체 스캔이 된다. 근본 해결은 인덱스지만,
# 백엔드 파드마다 기동 시 migrate 가 도는 구조라 CONCURRENTLY 마이그레이션은 별도 작업으로 둔다.
MAX_RANGE_DAYS = 400
DEFAULT_RANGE_DAYS = 365

TOP_PROBLEMS = 10
RECENT_QUESTIONS = 20

_LOGS = """
    SELECT
        l.id,
        l.user_id,
        l.problem_id,
        l.created_at,
        l.mode,
        l.student_question,
        l.student_language,
        l.student_code IS NOT NULL AS has_code,
        u.username,
        p._id      AS display_id,
        p.title,
        p.contest_id
    FROM problem_ai_hint_log l
    JOIN "user" u ON u.id = l.user_id
    JOIN problem p ON p.id = l.problem_id
    WHERE u.admin_type = %(regular)s
      AND btrim(l.hint_content) <> ''
      AND l.created_at >= %(start)s
      AND l.created_at < %(end)s
"""

# 채택률 분모용. 채점 상태는 따지지 않는다. 채점 대기를 빼면 채점이 밀릴수록
# 분모가 줄어 채택률이 저절로 올라간다.
_ENGAGED_SUBMISSIONS = """
    SELECT s.user_id, s.problem_id
    FROM submission s
    JOIN "user" u ON u.id = s.user_id
    JOIN problem p ON p.id = s.problem_id
    WHERE u.admin_type = %(regular)s
      AND p.contest_id IS NULL
      AND s.create_time >= %(start)s
      AND s.create_time < %(end)s
    GROUP BY s.user_id, s.problem_id
"""

# 지표를 한 문장으로 모아 한 행으로 돌려받는다.
_AGGREGATES = f"""
WITH logs AS ({_LOGS}),
practice AS (SELECT * FROM logs WHERE contest_id IS NULL),
contest_logs AS (SELECT * FROM logs WHERE contest_id IS NOT NULL),
practice_totals AS (
    SELECT
        count(*)                                  AS turns,
        count(*) FILTER (WHERE mode = %(chat)s)   AS chat_turns,
        count(DISTINCT user_id)                   AS users,
        count(DISTINCT problem_id)                AS problems
    FROM practice
),
contest_totals AS (
    SELECT
        count(*)                   AS turns,
        count(DISTINCT user_id)    AS users,
        count(DISTINCT contest_id) AS contests
    FROM contest_logs
),
adoption AS (
    -- 채택률: 일반 문제에 손을 댄 (사용자, 문제) 짝 중 몇 퍼센트가 AI 조교를 썼는가.
    -- 분모는 제출한 짝과 AI 조교를 쓴 짝의 합집합이다. 질문만 하고 제출하지 않은
    -- 경우가 있어 제출 짝만 분모로 쓰면 100%%를 넘을 수 있다.
    SELECT
        count(*) FILTER (WHERE hinted) AS hinted_pairs,
        count(*)                       AS engaged_pairs
    FROM (
        SELECT user_id, problem_id, bool_or(hinted) AS hinted
        FROM (
            SELECT DISTINCT user_id, problem_id, true AS hinted FROM practice
            UNION ALL
            SELECT user_id, problem_id, false FROM ({_ENGAGED_SUBMISSIONS}) s
        ) e
        GROUP BY user_id, problem_id
    ) x
),
top_problems AS (
    SELECT
        problem_id,
        display_id,
        title,
        count(*)                AS turns,
        count(DISTINCT user_id) AS users
    FROM practice
    GROUP BY problem_id, display_id, title
),
lifetime AS (
    -- 힌트 한도는 (사용자, 문제) 단위로 **평생** 누적된다. 조회 구간과 상관없이
    -- 원본 로그를 센다. 요청 제한(oj.py)처럼 빈 로그도 센다.
    -- 구간 끝까지만 세야 과거 구간을 다시 조회해도 같은 값이 나온다.
    SELECT a.contest_id, a.user_id, a.problem_id, count(l.id) AS lifetime_turns
    FROM (SELECT DISTINCT contest_id, user_id, problem_id FROM contest_logs) a
    JOIN problem_ai_hint_log l
      ON l.user_id = a.user_id AND l.problem_id = a.problem_id
     AND l.created_at < %(end)s
    GROUP BY a.contest_id, a.user_id, a.problem_id
),
contests AS (
    SELECT
        c.id                                                  AS contest_id,
        c.title,
        to_char(c.start_time AT TIME ZONE %(tz)s, 'YYYY-MM-DD') AS start_date,
        u.turns,
        u.users,
        u.problems,
        lim.pairs,
        lim.at_limit
    FROM (
        SELECT contest_id, count(*) AS turns, count(DISTINCT user_id) AS users,
               count(DISTINCT problem_id) AS problems
        FROM contest_logs GROUP BY contest_id
    ) u
    JOIN (
        SELECT contest_id, count(*) AS pairs,
               count(*) FILTER (WHERE lifetime_turns >= %(limit)s) AS at_limit
        FROM lifetime GROUP BY contest_id
    ) lim ON lim.contest_id = u.contest_id
    JOIN contest c ON c.id = u.contest_id
),
recent AS (
    SELECT
        id,
        to_char(created_at AT TIME ZONE %(tz)s, 'YYYY-MM-DD HH24:MI') AS created_at,
        display_id,
        title,
        username,
        student_question AS question,
        student_language AS language,
        has_code,
        created_at AS sort_key
    FROM practice
    WHERE mode = %(chat)s AND student_question IS NOT NULL
    ORDER BY created_at DESC, id DESC
    LIMIT %(recent)s
)
SELECT
    (SELECT row_to_json(t) FROM practice_totals t) AS practice,
    (SELECT row_to_json(t) FROM contest_totals t)  AS contest,
    (SELECT row_to_json(a) FROM adoption a)        AS adoption,
    -- problem_id 를 마지막 정렬 키로 둬야 동점일 때 새로고침마다 순서가 바뀌지 않는다.
    (SELECT coalesce(json_agg(tp ORDER BY tp.turns DESC, tp.users DESC, tp.problem_id), '[]'::json)
       FROM (SELECT * FROM top_problems
             ORDER BY turns DESC, users DESC, problem_id LIMIT %(top)s) tp) AS top_problems,
    (SELECT coalesce(json_agg(c ORDER BY c.start_date DESC, c.contest_id DESC), '[]'::json)
       FROM contests c)                                                     AS contests,
    (SELECT coalesce(json_agg(r ORDER BY r.sort_key DESC, r.id DESC), '[]'::json)
       FROM recent r)                                                       AS recent
"""

# 인덱스가 없어 넓은 구간 조회가 오래 걸릴 수 있다. 워커를 물고 있는 대신
# 빨리 실패하게 만든다. 관리자 화면이므로 몇 초를 넘기면 그 자체가 신호다.
STATEMENT_TIMEOUT_MS = 10_000


def _one(sql, params):
    # SET LOCAL 은 트랜잭션 블록 안에서만 유효하다. Django 는 기본이 autocommit 이라
    # atomic 으로 감싸지 않으면 경고만 남기고 조용히 무시된다.
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("SET LOCAL statement_timeout = %s", [STATEMENT_TIMEOUT_MS])
        cursor.execute(sql, params)
        row = cursor.fetchone()
        if row is None:
            return {}
        return dict(zip([col[0] for col in cursor.description], row))


def _rate(numerator, denominator, digits=1):
    if not denominator:
        return 0.0
    return round(100.0 * numerator / denominator, digits)


def mask_username(username):
    """앞 두 글자만 남긴다. 학번이면 입학 연도까지만 보인다."""
    keep = 2 if len(username) > 2 else 1
    return username[:keep] + "*" * (len(username) - keep)


class AIHintStatsAPI(APIView):
    """AI 조교 사용 현황을 한 번에 돌려준다.

    쿼리 파라미터
        start, end : YYYY-MM-DD. 생략하면 최근 1년. 최대 폭은 MAX_RANGE_DAYS 일.
    """

    @super_admin_required
    def get(self, request):
        try:
            start, end = self._parse_range(request)
        except (ValueError, OverflowError) as exc:
            # 9999-12-31 같은 경계 날짜는 timedelta 연산에서 OverflowError 를 낸다.
            message = str(exc) if isinstance(exc, ValueError) else "조회할 수 없는 날짜입니다."
            return self.error(message)

        agg = _one(_AGGREGATES, {
            "start": start,
            "end": end,
            "limit": HINT_LIMIT_PER_PROBLEM,
            "chat": AIHintMode.CHAT,
            "regular": AdminType.REGULAR_USER,
            # USE_TZ=True 이면 DB 세션 타임존이 UTC 다. 표시용 날짜는 현지 시각으로 바꾼다.
            "tz": settings.TIME_ZONE,
            "top": TOP_PROBLEMS,
            "recent": RECENT_QUESTIONS,
        })
        practice = agg.get("practice") or {}
        contest = agg.get("contest") or {}
        adoption = agg.get("adoption") or {}

        return self.success({
            "range": {
                "start": start.date().isoformat(),
                "end": (end - timedelta(days=1)).date().isoformat(),
                # 시작일과 종료일 사이로 허용되는 최대 간격(일). 클라이언트가 포함/배타 규칙을
                # 다시 계산하지 않도록 계산된 값을 그대로 보낸다.
                "max_range_span_days": MAX_RANGE_DAYS - 1,
            },
            "practice": {
                "turns": practice.get("turns") or 0,
                "chat_turns": practice.get("chat_turns") or 0,
                "users": practice.get("users") or 0,
                "problems": practice.get("problems") or 0,
                "hinted_pairs": adoption.get("hinted_pairs") or 0,
                "engaged_pairs": adoption.get("engaged_pairs") or 0,
                "adoption_rate": _rate(adoption.get("hinted_pairs") or 0,
                                       adoption.get("engaged_pairs") or 0),
            },
            "contest": {
                "turns": contest.get("turns") or 0,
                "users": contest.get("users") or 0,
                "contests": contest.get("contests") or 0,
                "limit": HINT_LIMIT_PER_PROBLEM,
            },
            "top_problems": agg.get("top_problems") or [],
            "contests": [
                {
                    "contest_id": c["contest_id"],
                    "title": c["title"],
                    "start_date": c["start_date"],
                    "turns": c["turns"],
                    "users": c["users"],
                    "problems": c["problems"],
                    "limit_reached_rate": _rate(c["at_limit"], c["pairs"]),
                }
                for c in agg.get("contests") or []
            ],
            "recent_questions": [
                {
                    "created_at": r["created_at"],
                    "display_id": r["display_id"],
                    "title": r["title"],
                    "user": mask_username(r["username"]),
                    "question": r["question"],
                    "language": r["language"],
                    "has_code": r["has_code"],
                }
                for r in agg.get("recent") or []
            ],
        })

    @staticmethod
    def _parse_range(request):
        raw_end = request.GET.get("end")
        raw_start = request.GET.get("start")

        # make_aware 는 naive 만 받으므로 계산이 끝날 때까지 naive 로 다룬다.
        if raw_end:
            try:
                end = datetime.strptime(raw_end, "%Y-%m-%d")
            except ValueError:
                raise ValueError("날짜 형식이 올바르지 않습니다. YYYY-MM-DD 로 보내주세요.")
        else:
            end = timezone.localtime().replace(tzinfo=None)
        # end 는 그 날을 포함해야 하므로 다음 날 0시를 배타 상한으로 쓴다.
        end = end.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        if raw_start:
            try:
                start = datetime.strptime(raw_start, "%Y-%m-%d")
            except ValueError:
                raise ValueError("날짜 형식이 올바르지 않습니다. YYYY-MM-DD 로 보내주세요.")
        else:
            start = end - timedelta(days=DEFAULT_RANGE_DAYS)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)

        if start >= end:
            raise ValueError("시작일이 종료일보다 앞서야 합니다.")
        if (end - start).days > MAX_RANGE_DAYS:
            raise ValueError(f"조회 구간은 최대 {MAX_RANGE_DAYS}일까지만 가능합니다.")

        current_tz = timezone.get_current_timezone()
        return timezone.make_aware(start, current_tz), timezone.make_aware(end, current_tz)
