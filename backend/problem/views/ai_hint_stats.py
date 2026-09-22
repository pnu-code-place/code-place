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
"""

import re
from datetime import datetime, timedelta

from django.conf import settings
from django.db import connection
from django.utils import timezone

from account.decorators import super_admin_required
from utils.api import APIView

# 이 간격을 넘겨 다시 요청하면 새 대화로 센다.
# 2026-09 운영 데이터(연속 요청 208건) 기준으로 정했다. 87.9%가 15분 이내에 몰려 있고
# 15~30분 구간은 0건이라 그 사이가 자연스러운 경계다. 15분과 30분은 결과가 같다.
SESSION_GAP_MINUTES = 30

# 문제당 힌트 횟수 제한. 챗봇 전환 시 사라지는 값이므로 여기 한 곳에만 둔다.
HINT_LIMIT_PER_PROBLEM = 5

# 프롬프트가 요구하는 응답 머리말. 예) "[2단계] ..."
# 이것도 단계 체계가 사라지면 함께 없어질 한시적 품질 지표다.
STAGE_LABEL_PATTERN = r"^\[[0-9]단계\]"

# 일반 사용자 로그만 집계한다. 관리자는 횟수 제한을 받지 않아 분포를 왜곡한다.
_BASE_LOGS = """
    SELECT l.id, l.user_id, l.problem_id, l.created_at, l.hint_content
    FROM problem_ai_hint_log l
    JOIN "user" u ON u.id = l.user_id
    WHERE u.admin_type = 'Regular User'
      AND u.is_disabled = false
      AND l.created_at >= %(start)s
      AND l.created_at < %(end)s
"""

# 로그에 세션 번호와 세션 내 턴 번호를 붙인다. 아래 집계들이 모두 이 결과에서 파생된다.
_TURNS_CTE = f"""
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
turns AS (
    SELECT *,
        SUM(new_session) OVER (
            PARTITION BY user_id, problem_id ORDER BY created_at
        ) AS session_no
    FROM gaps
)
"""


def _rows(sql, params):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _one(sql, params):
    rows = _rows(sql, params)
    return rows[0] if rows else {}


def _rate(numerator, denominator, digits=1):
    if not denominator:
        return 0.0
    return round(100.0 * numerator / denominator, digits)


class AIHintStatsAPI(APIView):
    """AI 조교 사용량과 효과를 한 번에 돌려준다.

    쿼리 파라미터
        start, end : YYYY-MM-DD. 생략하면 최근 12개월.
    """

    @super_admin_required
    def get(self, request):
        try:
            start, end = self._parse_range(request)
        except ValueError:
            return self.error("날짜가 올바르지 않습니다. YYYY-MM-DD 형식이어야 하고 시작일이 종료일보다 앞서야 합니다.")

        params = {
            "start": start,
            "end": end,
            "gap": f"{SESSION_GAP_MINUTES} minutes",
            "limit": HINT_LIMIT_PER_PROBLEM,
            "label": STAGE_LABEL_PATTERN,
            # USE_TZ=True 이면 Django 가 DB 세션 타임존을 UTC 로 잡는다.
            # 월 경계와 시간대 분포는 현지 시각 기준이어야 하므로 명시적으로 변환한다.
            "tz": settings.TIME_ZONE,
        }

        return self.success({
            "range": {
                "start": start.date().isoformat(),
                "end": (end - timedelta(days=1)).date().isoformat(),
                "session_gap_minutes": SESSION_GAP_MINUTES,
            },
            "summary": self._summary(params),
            "monthly": self._monthly(params),
            "hourly": self._hourly(params),
            "depth": self._depth(params),
            "effect": self._effect(params),
            "quality": self._quality(params),
            "top_problems": self._top_problems(params),
        })

    @staticmethod
    def _parse_range(request):
        raw_end = request.GET.get("end")
        raw_start = request.GET.get("start")

        # make_aware 는 naive 만 받으므로 계산이 끝날 때까지 naive 로 다룬다.
        if raw_end:
            end = datetime.strptime(raw_end, "%Y-%m-%d")
        else:
            end = timezone.localtime().replace(tzinfo=None)
        # end 는 그 날을 포함해야 하므로 다음 날 0시를 배타 상한으로 쓴다.
        end = end.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        if raw_start:
            start = datetime.strptime(raw_start, "%Y-%m-%d")
        else:
            start = end - timedelta(days=365)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)

        if start >= end:
            raise ValueError("start must be before end")

        current_tz = timezone.get_current_timezone()
        return timezone.make_aware(start, current_tz), timezone.make_aware(end, current_tz)

    # --- 요약 -----------------------------------------------------------

    def _summary(self, params):
        row = _one(_TURNS_CTE + """
            SELECT
                count(*)                                       AS turns,
                count(DISTINCT (user_id, problem_id, session_no)) AS sessions,
                count(DISTINCT user_id)                        AS users,
                count(DISTINCT problem_id)                     AS problems,
                count(*) FILTER (WHERE btrim(hint_content) = '') AS empty_turns
            FROM turns
        """, params)

        # 채택률: 문제에 손을 댄 (사용자, 문제) 쌍 중 몇 퍼센트가 AI 조교를 썼는가.
        # 분모는 제출한 쌍과 힌트를 받은 쌍의 합집합이다. 힌트만 받고 제출하지 않은
        # 경우가 있어 제출 쌍만 분모로 쓰면 비율이 100%를 넘을 수 있다.
        adoption = _one("""
            SELECT
                count(*) FILTER (WHERE hinted) AS hinted_pairs,
                count(*)                       AS engaged_pairs
            FROM (
                SELECT user_id, problem_id, bool_or(hinted) AS hinted
                FROM (
                    SELECT l.user_id, l.problem_id, true AS hinted
                    FROM problem_ai_hint_log l
                    JOIN "user" u ON u.id = l.user_id
                    WHERE u.admin_type = 'Regular User' AND u.is_disabled = false
                      AND l.created_at >= %(start)s AND l.created_at < %(end)s
                    UNION ALL
                    SELECT s.user_id, s.problem_id, false
                    FROM submission s
                    JOIN "user" u ON u.id = s.user_id
                    WHERE u.admin_type = 'Regular User' AND u.is_disabled = false
                      AND s.contest_id IS NULL
                      AND s.create_time >= %(start)s AND s.create_time < %(end)s
                ) engaged
                GROUP BY user_id, problem_id
            ) x
        """, params)

        turns = row.get("turns") or 0
        return {
            "turns": turns,
            "sessions": row.get("sessions") or 0,
            "users": row.get("users") or 0,
            "problems": row.get("problems") or 0,
            "failure_rate": _rate(row.get("empty_turns") or 0, turns),
            "hinted_pairs": adoption.get("hinted_pairs") or 0,
            "engaged_pairs": adoption.get("engaged_pairs") or 0,
            "adoption_rate": _rate(adoption.get("hinted_pairs") or 0,
                                   adoption.get("engaged_pairs") or 0),
        }

    # --- 추이 -----------------------------------------------------------

    def _monthly(self, params):
        return _rows(_TURNS_CTE + """
            SELECT
                to_char(date_trunc('month', created_at AT TIME ZONE %(tz)s), 'YYYY-MM') AS month,
                count(*)                                            AS turns,
                count(DISTINCT (user_id, problem_id, session_no))   AS sessions,
                count(DISTINCT user_id)                             AS users
            FROM turns
            GROUP BY 1
            ORDER BY 1
        """, params)

    def _hourly(self, params):
        found = {
            int(r["hour"]): r["turns"]
            for r in _rows(_TURNS_CTE + """
                SELECT EXTRACT(HOUR FROM created_at AT TIME ZONE %(tz)s) AS hour, count(*) AS turns
                FROM turns GROUP BY 1
            """, params)
        }
        return [{"hour": h, "turns": found.get(h, 0)} for h in range(24)]

    # --- 대화 깊이 ------------------------------------------------------

    def _depth(self, params):
        """세션당 몇 턴을 주고받았는지. 챗봇으로 바뀌어도 그대로 쓰는 지표다."""
        buckets = _rows(_TURNS_CTE + """
            , per_session AS (
                SELECT user_id, problem_id, session_no, count(*) AS turns
                FROM turns
                GROUP BY user_id, problem_id, session_no
            )
            SELECT turns, count(*) AS sessions
            FROM per_session
            GROUP BY turns
            ORDER BY turns
        """, params)

        # 힌트 횟수 제한은 (사용자, 문제) 단위로 평생 누적된다. 세션 단위가 아니다.
        # 5회를 며칠에 걸쳐 나눠 쓰면 세션마다는 1~2턴이지만 한도는 채운 것이므로
        # 여기만 세션이 아닌 (사용자, 문제) 기준으로 센다.
        limit_row = _one(_TURNS_CTE + """
            , per_pair AS (
                SELECT user_id, problem_id, count(*) AS turns
                FROM turns
                GROUP BY user_id, problem_id
            )
            SELECT
                count(*)                                        AS pairs,
                count(*) FILTER (WHERE turns >= %(limit)s)      AS at_limit
            FROM per_pair
        """, params)

        total_sessions = sum(b["sessions"] for b in buckets)
        total_turns = sum(b["turns"] * b["sessions"] for b in buckets)
        single = next((b["sessions"] for b in buckets if b["turns"] == 1), 0)

        return {
            "distribution": [{"turns": b["turns"], "sessions": b["sessions"]} for b in buckets],
            "sessions": total_sessions,
            "avg_turns": round(total_turns / total_sessions, 2) if total_sessions else 0.0,
            "single_turn_rate": _rate(single, total_sessions),
            # 한도가 사라지면 아래 두 값만 의미를 잃는다.
            "limit_reached_rate": _rate(limit_row.get("at_limit") or 0, limit_row.get("pairs") or 0),
            "limit": HINT_LIMIT_PER_PROBLEM,
        }

    # --- 효과 -----------------------------------------------------------

    def _effect(self, params):
        """힌트를 받은 뒤 정답에 도달한 비율과, 힌트를 쓰지 않은 경우의 비율.

        주의: 두 집단은 무작위로 나뉘지 않았다. 힌트를 쓰는 학생과 쓰지 않는 학생의
        성향 차이가 그대로 섞여 있으므로 인과관계로 읽으면 안 된다.
        화면에서도 표본 수와 함께 보여주고 주의 문구를 붙인다.
        """
        with_hint = _one("""
            SELECT count(*) AS pairs, count(*) FILTER (WHERE solved) AS accepted
            FROM (
                SELECT h.user_id, h.problem_id, EXISTS (
                    SELECT 1 FROM submission s
                    WHERE s.user_id = h.user_id
                      AND s.problem_id = h.problem_id
                      AND s.contest_id IS NULL
                      AND s.result = 0
                      AND s.create_time > h.first_hint
                ) AS solved
                FROM (
                    SELECT l.user_id, l.problem_id, min(l.created_at) AS first_hint
                    FROM problem_ai_hint_log l
                    JOIN "user" u ON u.id = l.user_id
                    WHERE u.admin_type = 'Regular User' AND u.is_disabled = false
                      AND l.created_at >= %(start)s AND l.created_at < %(end)s
                    GROUP BY l.user_id, l.problem_id
                ) h
            ) x
        """, params)

        without_hint = _one("""
            SELECT count(*) AS pairs, count(*) FILTER (WHERE solved) AS accepted
            FROM (
                SELECT s.user_id, s.problem_id, bool_or(s.result = 0) AS solved
                FROM submission s
                JOIN "user" u ON u.id = s.user_id
                WHERE u.admin_type = 'Regular User' AND u.is_disabled = false
                  AND s.contest_id IS NULL
                  AND s.create_time >= %(start)s AND s.create_time < %(end)s
                  AND NOT EXISTS (
                      SELECT 1 FROM problem_ai_hint_log l
                      WHERE l.user_id = s.user_id AND l.problem_id = s.problem_id
                  )
                GROUP BY s.user_id, s.problem_id
            ) x
        """, params)

        def shape(row):
            pairs = row.get("pairs") or 0
            accepted = row.get("accepted") or 0
            return {"pairs": pairs, "accepted": accepted, "rate": _rate(accepted, pairs)}

        return {"with_hint": shape(with_hint), "without_hint": shape(without_hint)}

    # --- 응답 품질 ------------------------------------------------------

    def _quality(self, params):
        row = _one(_TURNS_CTE + """
            SELECT
                count(*)                                                    AS turns,
                count(*) FILTER (WHERE btrim(hint_content) = '')            AS empty,
                count(*) FILTER (WHERE btrim(hint_content) ~ %(label)s)     AS labeled,
                percentile_disc(0.5) WITHIN GROUP (ORDER BY length(hint_content)) AS len_p50,
                percentile_disc(0.9) WITHIN GROUP (ORDER BY length(hint_content)) AS len_p90,
                max(length(hint_content))                                   AS len_max
            FROM turns
        """, params)

        turns = row.get("turns") or 0
        empty = row.get("empty") or 0
        answered = turns - empty
        return {
            "turns": turns,
            "empty": empty,
            "failure_rate": _rate(empty, turns),
            "length": {
                "p50": row.get("len_p50") or 0,
                "p90": row.get("len_p90") or 0,
                "max": row.get("len_max") or 0,
            },
            # 단계 라벨은 프롬프트가 지시한 형식이다. 챗봇 전환 시 함께 걷어낸다.
            "labeled": row.get("labeled") or 0,
            "label_rate": _rate(row.get("labeled") or 0, answered),
        }

    # --- 문제별 -------------------------------------------------------

    def _top_problems(self, params):
        """요청이 몰리는 문제는 학생들이 막히는 지점이다."""
        return _rows(_TURNS_CTE + """
            SELECT
                p.id                                              AS problem_id,
                p._id                                             AS display_id,
                p.title                                           AS title,
                count(*)                                          AS turns,
                count(DISTINCT t.user_id)                         AS users,
                count(DISTINCT (t.user_id, t.problem_id, t.session_no)) AS sessions
            FROM turns t
            JOIN problem p ON p.id = t.problem_id
            GROUP BY p.id, p._id, p.title
            ORDER BY turns DESC, users DESC
            LIMIT 10
        """, params)


def is_stage_labeled(hint_content):
    """응답이 프롬프트가 요구한 `[N단계]` 머리말을 지켰는지.

    SQL 쪽 `STAGE_LABEL_PATTERN` 과 같은 판정을 파이썬에서 쓰기 위한 헬퍼다.
    """
    return bool(re.match(STAGE_LABEL_PATTERN, (hint_content or "").strip()))
