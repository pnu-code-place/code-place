"""AI 조교 사용 현황 집계.

`ProblemAIHintLog` 에는 (user, problem, hint_content, created_at) 네 가지만 쌓인다.
단계 번호, 모델 이름, 응답 시간 같은 컬럼은 없다.
그래서 지표는 전부 이 네 가지에서 파생시킨다.

핵심 추상은 **세션과 턴**이다. 지금은 문제 하나당 힌트를 최대 5번 받는 구조지만,
나중에 챗봇으로 바뀌어도 "한 번 앉아서 주고받은 묶음(세션)"과 "그 안의 발화(턴)"라는
개념은 그대로 유지된다. 단계(1~5)를 1급 개념으로 쓰지 않는 이유다.

세션 경계는 시간 간격으로 정의한다. 같은 (user, problem) 에서 연속된 로그의 간격이
SESSION_GAP_MINUTES 를 넘으면 다른 세션으로 본다. 며칠 뒤 같은 문제를 다시 물어본 것을
한 대화로 묶지 않기 위함이다.

집계 범위에 대한 결정
---------------------
**대회 문제는 모든 지표에서 제외한다.** 대회는 AI 조교가 기본 비활성이고 풀이 역학도
연습 문제와 다르다. 무엇보다 힌트 쪽과 제출 쪽의 필터가 어긋나면 "힌트는 세는데 정답은
빠지는" 짝이 생겨 채택률과 정답 도달률이 동시에 왜곡된다. 양쪽을 같은 기준
(`problem.contest_id`)으로 맞춘다.

**관리자 로그도 제외한다.** 관리자는 횟수 제한을 받지 않아 분포를 왜곡한다.
반대로 `is_disabled` 는 거르지 않는다. 계정이 나중에 비활성화되면 이미 지나간 달의
수치가 소급해서 바뀌기 때문이다.

알려진 한계: `admin_type` 도 지금 값을 보므로 같은 성질이 남아 있다. 학생이 나중에
조교로 승격되면 그가 학생일 때 쌓은 기록이 과거 구간에서도 사라진다. 로그 행에
당시 역할을 남기지 않는 한 완전한 재현성은 얻을 수 없다.

**학습 효과(정답 도달률) 비교는 넣지 않는다.** "AI 조교를 써서 더 잘 풀었는가"는
어떤 짝을 모집단에 넣느냐에 따라 결과가 뒤집힌다. 구간 이전의 힌트, 구간 이전의 정답,
힌트를 누르기 전에 이미 푼 경우, 제출 없이 힌트만 받은 경우, 채점이 끝나지 않은 제출 —
각각을 어떻게 다루느냐가 그대로 숫자를 좌우한다. 무작위 배정도 아니어서 인과로 읽을 수도
없다. 객관적인 수치로 제시하기 어려운 지표이므로, 방법론을 먼저 합의한 뒤 별도로 만든다.

**채택률의 분모는 조회 구간 전체다.** AI 조교가 없던 시기를 포함해 조회하면
분모에는 들어가고 분자에는 못 들어가므로 채택률이 실제보다 낮게 나온다.
기능 시작 시점을 자동으로 잡아 보정하려면 힌트 로그 전체를 훑어야 하는데,
그 비용이 보정 효과보다 커서 넣지 않았다. 기능 도입 전후를 함께 보는 구간이라면
이 점을 감안해서 읽어야 한다.

**내용이 빈 로그도 제외한다.** 스트리밍 시작 전에 선점 생성되는 행이라
정상 경로에서는 `_persist_hint_log` 가 지우지만, 워커가 중간에 죽으면 그대로 남는다.
그런 행을 세면 없던 턴이 생기고 응답 길이와 형식 준수율이 함께 내려간다.
"""

from datetime import datetime, timedelta

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

from account.decorators import super_admin_required
from account.models import AdminType
from utils.api import APIView

from utils.constants import HINT_LIMIT_PER_PROBLEM

from ..llm_hint import STAGE_LABEL_PATTERN

# 이 간격을 넘겨 다시 요청하면 새 대화로 센다.
# 2026-09 운영 데이터(연속 요청 208건) 기준으로 정했다. 87.9%가 15분 이내에 몰려 있고
# 15~30분 구간은 0건이라 그 사이가 자연스러운 경계다. 15분과 30분은 결과가 같다.
SESSION_GAP_MINUTES = 30

# 응답 머리말 규칙은 프롬프트가 소유한다(`llm_hint.STAGE_LABEL_PATTERN`).
# 프롬프트를 고치면 이 지표가 조용히 0% 로 떨어지므로 정의를 한 곳에 둔다.

# `submission.create_time` 에 인덱스가 없고, `problem_ai_hint_log` 의 인덱스는 전부
# `user`/`problem` 으로 시작해서 `created_at` 단독 범위 조건으로는 탐색이 안 된다.
# 그래서 조회 구간이 넓으면 양쪽 다 전체 스캔이 된다.
# 근본 해결은 `create_time` 인덱스다. 다만 백엔드 파드가 여러 개이고 기동마다
# `manage.py migrate` 가 도는 구조라, CONCURRENTLY 마이그레이션을 이 PR 에 섞으면
# 동시 실행으로 INVALID 인덱스가 남을 수 있다. 인덱스는 별도 작업으로 분리한다.
MAX_RANGE_DAYS = 400
DEFAULT_RANGE_DAYS = 365

# 모집단 조건. 여섯 개 쿼리가 **같은 기준**을 써야 "힌트는 세는데 정답은 빠지는"
# 짝이 생기지 않는다. 조건을 바꿀 일이 있으면 이 두 조각만 고친다.
_LOG_POPULATION = """
    FROM problem_ai_hint_log l
    JOIN "user" u ON u.id = l.user_id
    JOIN problem p ON p.id = l.problem_id
    WHERE u.admin_type = %(regular)s
      AND p.contest_id IS NULL
      AND btrim(l.hint_content) <> ''
"""

_SUB_POPULATION = """
    FROM submission s
    JOIN "user" u ON u.id = s.user_id
    JOIN problem p ON p.id = s.problem_id
    WHERE u.admin_type = %(regular)s
      AND p.contest_id IS NULL
"""

# 일반 사용자의, 내용이 있는, 연습 문제 힌트만 본다. 모듈 주석의 "집계 범위" 참고.
_BASE_LOGS = f"""
    SELECT
        l.user_id,
        l.problem_id,
        l.created_at,
        length(l.hint_content)            AS content_length,
        l.hint_content ~ %(label)s        AS labeled
{_LOG_POPULATION.rstrip()}
      -- 구간 양쪽으로 gap 만큼 더 읽는다. 앞쪽은 LAG 가 앞 턴을 보기 위해,
      -- 뒤쪽은 구간 끝에서 시작한 대화가 한도까지 이어져도 잘리지 않을 만큼이다.
      -- 이 여분 행들은 아래에서 지표별로 걸러낸다.
      AND l.created_at >= %(start)s::timestamptz - %(gap)s::interval
      AND l.created_at < %(end)s::timestamptz + %(tail)s::interval
"""

# 기간 안의 연습 문제 제출. 채택률("문제에 손을 댔나")은 채점 상태를 따지지 않는다.
# 채점 대기를 빼면 채점이 밀릴수록 분모가 줄어 채택률이 저절로 올라간다.
_ENGAGED_SUBMISSIONS = f"""
    SELECT s.user_id, s.problem_id
{_SUB_POPULATION.rstrip()}
      AND s.create_time >= %(start)s
      AND s.create_time < %(end)s
    GROUP BY s.user_id, s.problem_id
"""

# 턴 단위 지표를 한 문장으로 낸다.
# 지표마다 CTE 를 따로 붙이면 같은 윈도 함수 파이프라인을 대여섯 번 다시 돈다.
# 여기서는 turns 를 한 번만 만들고 각 집계를 JSON 으로 모아 한 행으로 돌려받는다.
_TURN_AGGREGATES = f"""
WITH logs AS ({_BASE_LOGS}),
gaps AS (
    SELECT *,
        CASE
            WHEN LAG(created_at) OVER w IS NULL
              OR created_at - LAG(created_at) OVER w > %(gap)s::interval
            THEN 1 ELSE 0
        END AS new_session
    FROM logs
    WINDOW w AS (PARTITION BY user_id, problem_id ORDER BY created_at)
),
numbered AS (
    SELECT *,
        SUM(new_session) OVER (
            PARTITION BY user_id, problem_id ORDER BY created_at
        ) AS session_no
    FROM gaps
),
scoped AS (
    SELECT *,
        MIN(created_at) OVER (PARTITION BY user_id, problem_id, session_no) AS session_start
    FROM numbered
),
turns AS (
    -- 턴 지표: 구간 안에서 일어난 턴만 센다. 양옆에서 읽어 온 여분 행을 뺀다.
    SELECT * FROM scoped
    WHERE created_at >= %(start)s AND created_at < %(end)s
),
session_turns AS (
    -- 세션 지표: **구간 안에서 시작한 대화**의 턴 전부. 구간 밖으로 이어진 꼬리까지
    -- 포함해야 대화 깊이가 실제대로 나온다. 걸친 대화를 양쪽에서 세면 구간을
    -- 좁힐수록 세션 수가 부풀고 월별 합계가 요약 카드와 어긋난다.
    SELECT * FROM scoped
    WHERE session_start >= %(start)s AND session_start < %(end)s
),
totals AS (
    SELECT
        count(*)                                                 AS turns,
        (SELECT count(DISTINCT (user_id, problem_id, session_no)) FROM session_turns) AS sessions,
        count(DISTINCT user_id)                                  AS users,
        count(DISTINCT problem_id)                               AS problems,
        count(*) FILTER (WHERE labeled)                           AS labeled,
        percentile_disc(0.5) WITHIN GROUP (ORDER BY content_length) AS len_p50,
        percentile_disc(0.9) WITHIN GROUP (ORDER BY content_length) AS len_p90,
        coalesce(max(content_length), 0)                          AS len_max
    FROM turns
),
monthly AS (
    SELECT
        to_char(date_trunc('month', created_at AT TIME ZONE %(tz)s), 'YYYY-MM') AS month,
        count(*)                                          AS turns,
        count(DISTINCT user_id)                           AS users
    FROM turns
    GROUP BY 1
),
monthly_sessions AS (
    -- 대화는 시작한 달에 한 번만 센다. 턴이 속한 달로 세면 월 경계를 걸친 대화가
    -- 두 달에 각각 잡혀 월별 합계가 요약 카드와 달라진다.
    SELECT
        to_char(date_trunc('month', session_start AT TIME ZONE %(tz)s), 'YYYY-MM') AS month,
        count(*) AS sessions
    FROM (SELECT DISTINCT user_id, problem_id, session_no, session_start FROM session_turns) x
    GROUP BY 1
),
month_axis AS (
    SELECT to_char(m, 'YYYY-MM') AS month
    FROM generate_series(
        date_trunc('month', %(start)s::timestamptz AT TIME ZONE %(tz)s),
        date_trunc('month', (%(end)s::timestamptz - interval '1 second') AT TIME ZONE %(tz)s),
        interval '1 month'
    ) m
),
monthly_filled AS (
    -- 비어 있는 달을 건너뛰면 선 그래프가 떨어진 두 달을 이어 붙여
    -- 공백이 한 달의 등락처럼 그려진다.
    SELECT
        ax.month,
        coalesce(mo.turns, 0)    AS turns,
        coalesce(mo.users, 0)    AS users,
        coalesce(ms.sessions, 0) AS sessions
    FROM month_axis ax
    LEFT JOIN monthly mo          ON mo.month = ax.month
    LEFT JOIN monthly_sessions ms ON ms.month = ax.month
),
hourly AS (
    SELECT EXTRACT(HOUR FROM created_at AT TIME ZONE %(tz)s)::int AS hour, count(*) AS turns
    FROM turns
    GROUP BY 1
),
per_session AS (
    SELECT user_id, problem_id, session_no, count(*) AS turns
    FROM session_turns
    GROUP BY user_id, problem_id, session_no
),
depth AS (
    SELECT turns, count(*) AS sessions FROM per_session GROUP BY turns
),
lifetime AS (
    -- 힌트 횟수 제한은 (사용자, 문제) 단위로 **평생** 누적된다. 세션 단위도 조회 구간
    -- 단위도 아니므로, 한도 판정만 구간 필터가 걸리지 않은 원본 로그를 센다.
    -- 요청 제한(oj.py)은 빈 로그까지 포함해 세므로 여기서도 같은 기준으로 센다.
    -- 조회 구간 종료 시점까지만 보아야 과거 구간을 다시 조회해도 같은 값이 나온다.
    SELECT a.user_id, a.problem_id, count(l.id) AS lifetime_turns
    FROM (SELECT DISTINCT user_id, problem_id FROM turns) a
    JOIN problem_ai_hint_log l
      ON l.user_id = a.user_id AND l.problem_id = a.problem_id
     AND l.created_at < %(end)s
    GROUP BY a.user_id, a.problem_id
),
limits AS (
    SELECT
        count(*)                                            AS pairs,
        count(*) FILTER (WHERE lifetime_turns >= %(limit)s) AS at_limit
    FROM lifetime
),
adoption AS (
    -- 채택률: 문제에 손을 댄 (사용자, 문제) 짝 중 몇 퍼센트가 AI 조교를 썼는가.
    -- 분모는 제출한 짝과 힌트를 받은 짝의 합집합이다. 힌트만 받고 제출하지 않은
    -- 경우가 있어 제출 짝만 분모로 쓰면 비율이 100%%를 넘을 수 있다.
    SELECT
        count(*) FILTER (WHERE hinted) AS hinted_pairs,
        count(*)                       AS engaged_pairs
    FROM (
        SELECT user_id, problem_id, bool_or(hinted) AS hinted
        FROM (
            SELECT DISTINCT user_id, problem_id, true AS hinted FROM turns
            UNION ALL
            SELECT user_id, problem_id, false FROM ({_ENGAGED_SUBMISSIONS}) s
        ) e
        GROUP BY user_id, problem_id
    ) x
),
top_problems AS (
    SELECT
        p.id      AS problem_id,
        p._id     AS display_id,
        p.title   AS title,
        count(*)  AS turns,
        count(DISTINCT t.user_id) AS users,
        count(DISTINCT (t.user_id, t.problem_id, t.session_no))
            FILTER (WHERE t.session_start >= %(start)s)          AS sessions
    FROM turns t
    JOIN problem p ON p.id = t.problem_id
    GROUP BY p.id, p._id, p.title
    -- p.id 를 마지막 정렬 키로 둬야 동점일 때 새로고침마다 순서가 바뀌지 않는다.
    ORDER BY turns DESC, users DESC, p.id
    LIMIT 10
)
SELECT
    (SELECT row_to_json(t) FROM totals t)                                      AS totals,
    (SELECT coalesce(json_agg(m ORDER BY m.month), '[]'::json)
       FROM monthly_filled m)                                                  AS monthly,
    (SELECT coalesce(json_agg(h ORDER BY h.hour), '[]'::json) FROM hourly h)   AS hourly,
    (SELECT coalesce(json_agg(d ORDER BY d.turns), '[]'::json) FROM depth d)   AS depth,
    (SELECT row_to_json(l) FROM limits l)                                      AS limits,
    (SELECT row_to_json(a) FROM adoption a)                                    AS adoption,
    (SELECT coalesce(json_agg(tp ORDER BY tp.turns DESC, tp.users DESC, tp.problem_id),
                     '[]'::json) FROM top_problems tp)                         AS top_problems
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


class AIHintStatsAPI(APIView):
    """AI 조교 사용량과 효과를 한 번에 돌려준다.

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

        params = {
            "start": start,
            "end": end,
            "gap": f"{SESSION_GAP_MINUTES} minutes",
            # 대화 하나는 최대 HINT_LIMIT_PER_PROBLEM 턴이고 턴 사이 간격은 gap 미만이다.
            # 구간 끝에서 시작한 대화가 잘리지 않으려면 그만큼 뒤까지 읽어야 한다.
            # 가정: 한 대화의 턴 수가 한도를 넘지 않는다. 관리자는 한도를 받지 않으므로
            # 관리자였다가 일반 사용자로 바뀐 계정의 과거 기록은 잘릴 수 있다.
            "tail": f"{SESSION_GAP_MINUTES * (HINT_LIMIT_PER_PROBLEM - 1)} minutes",
            "limit": HINT_LIMIT_PER_PROBLEM,
            "label": STAGE_LABEL_PATTERN,
            "regular": AdminType.REGULAR_USER,
            # USE_TZ=True 이면 Django 가 DB 세션 타임존을 UTC 로 잡는다.
            # 월 경계와 시간대 분포는 현지 시각 기준이어야 하므로 명시적으로 변환한다.
            "tz": settings.TIME_ZONE,
        }

        agg = _one(_TURN_AGGREGATES, params)
        totals = agg.get("totals") or {}

        return self.success({
            "range": {
                "start": start.date().isoformat(),
                "end": (end - timedelta(days=1)).date().isoformat(),
                "session_gap_minutes": SESSION_GAP_MINUTES,
                # 시작일과 종료일 사이로 허용되는 최대 간격(일). 클라이언트가 포함/배타 규칙을
                # 다시 계산하지 않도록 계산된 값을 그대로 보낸다.
                "max_range_span_days": MAX_RANGE_DAYS - 1,
            },
            "summary": self._summary(totals, agg.get("adoption") or {}),
            "monthly": agg.get("monthly") or [],
            "hourly": self._fill_hours(agg.get("hourly") or []),
            "depth": self._depth(agg.get("depth") or [], agg.get("limits") or {}),
            "quality": self._quality(totals),
            "top_problems": agg.get("top_problems") or [],
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

    # --- 요약 -----------------------------------------------------------

    def _summary(self, totals, adoption):
        return {
            "turns": totals.get("turns") or 0,
            "sessions": totals.get("sessions") or 0,
            "users": totals.get("users") or 0,
            "problems": totals.get("problems") or 0,
            "hinted_pairs": adoption.get("hinted_pairs") or 0,
            "engaged_pairs": adoption.get("engaged_pairs") or 0,
            "adoption_rate": _rate(adoption.get("hinted_pairs") or 0,
                                   adoption.get("engaged_pairs") or 0),
        }

    # --- 추이 -----------------------------------------------------------

    @staticmethod
    def _fill_hours(rows):
        found = {int(r["hour"]): r["turns"] for r in rows}
        return [{"hour": h, "turns": found.get(h, 0)} for h in range(24)]

    # --- 대화 깊이 ------------------------------------------------------

    @staticmethod
    def _depth(buckets, limits):
        """세션당 몇 턴을 주고받았는지. 챗봇으로 바뀌어도 그대로 쓰는 지표다."""
        total_sessions = sum(b["sessions"] for b in buckets)
        total_turns = sum(b["turns"] * b["sessions"] for b in buckets)
        single = next((b["sessions"] for b in buckets if b["turns"] == 1), 0)
        return {
            "distribution": buckets,
            "avg_turns": round(total_turns / total_sessions, 2) if total_sessions else 0.0,
            "single_turn_rate": _rate(single, total_sessions),
            # 한도가 사라지면 아래 두 값만 의미를 잃는다.
            "limit_reached_rate": _rate(limits.get("at_limit") or 0, limits.get("pairs") or 0),
            "limit": HINT_LIMIT_PER_PROBLEM,
        }

    # --- 응답 품질 ------------------------------------------------------

    @staticmethod
    def _quality(totals):
        """응답 형식과 길이.

        "응답 실패율"은 여기서 낼 수 없다. `ProblemLLMHintAPI._persist_hint_log` 가
        빈 응답일 때 로그 행 자체를 지우므로(횟수도 환불된다) 실패한 요청은 테이블에
        남지 않는다. 실패 신호는 Prometheus 의 `AI_HINT_API_OUTCOME_TOTAL`
        (`empty_response` / `llm_error`)에 있고, 그건 Grafana 가 볼 영역이다.
        """
        turns = totals.get("turns") or 0
        return {
            "length": {
                "p50": totals.get("len_p50") or 0,
                "p90": totals.get("len_p90") or 0,
                "max": totals.get("len_max") or 0,
            },
            # 단계 라벨은 프롬프트가 지시한 형식이다. 챗봇 전환 시 함께 걷어낸다.
            "label_rate": _rate(totals.get("labeled") or 0, turns),
        }
