class Choices:

    @classmethod
    def choices(cls):
        d = cls.__dict__
        return [d[item] for item in d.keys() if not item.startswith("__")]


class ContestType:
    PUBLIC_CONTEST = "Public"
    PASSWORD_PROTECTED_CONTEST = "Password Protected"


class ContestStatus:
    CONTEST_NOT_START = "1"
    CONTEST_ENDED = "-1"
    CONTEST_UNDERWAY = "0"


class ContestRuleType(Choices):
    ACM = "ACM"
    OI = "OI"


class CacheKey:
    waiting_queue = "waiting_queue"
    contest_rank_cache = "contest_rank_cache:v2"
    website_config = "website_config"


class Difficulty(Choices):
    VERYLOW = "VeryLow"
    LOW = "Low"
    MID = "Mid"
    HIGH = "High"
    VERYHIGH = "VeryHigh"


CONTEST_PASSWORD_SESSION_KEY = "contest_password"

BANNER_VISIBLE_LIMIT = 5
POPUP_VISIBLE_LIMIT = 3

CONTENT_WIDTH_UPPER_BOUND = 1000
CONTENT_WIDTH_LOWER_BOUND = 200

RSS_FEED_URL = "https://swedu.pusan.ac.kr/bbs/swedu/2265/rssList.do?row=50"

GENERATE_MOCK_USERNAME_URL = "https://www.rivestsoft.com/nickname/getRandomNickname.ajax"

EMAIL_SUFFIX = "@pusan.ac.kr"

UNDEFINED_SMTP_USER = "Client"


class ProblemField:
    fields = ['implementation', 'math', 'datastructure', 'search', 'sorting', 'algorithm']
    strToInt = {
        'implementation': 0,
        'math': 1,
        'datastructure': 2,
        'search': 3,
        'sorting': 4,
        'algorithm': 5,
    }
    intToStr = {0: 'implementation', 1: 'math', 2: 'datastructure', 3: 'search', 4: 'sorting', 5: 'algorithm'}


class ProblemScore:
    score = {
        'VeryLow': 10,    # VeryLow
        'Low': 20,    # Low
        'Mid': 160,    # Mid
        'High': 640,    # High
        'VeryHigh': 1280,    # VeryHigh
    }


class Tier:
    tiers = {   # 티어별 시작 점수
        'sprout': 0,
        'bronze3': 100,
        'bronze2': 300,
        'bronze1': 500,
        'silver3': 700,
        'silver2': 1100,
        'silver1': 1500,
        'gold3': 1900,
        'gold2': 3500,
        'gold1': 5100,
        'platinum3': 6700,
        'platinum2': 13100,
        'platinum1': 19500,
        'diamond3': 25900,
        'diamond2': 38700,
        'diamond1': 51500,
    }

    @classmethod
    def next_tier(cls, current_tier):
        tiers_list = list(cls.tiers.keys())
        try:
            current_idx = tiers_list.index(current_tier)
            new_tier = tiers_list[current_idx + 1]
            new_current_score = cls.tiers[new_tier]
            new_next_score = cls.tiers[tiers_list[current_idx + 2]] if new_tier != 'diamond1' else None
            return new_tier, new_current_score, new_next_score
        except IndexError:
            return None


# 문제 하나당 받을 수 있는 AI 조교 힌트 횟수. (사용자, 문제) 단위로 평생 누적된다.
# 요청 제한(problem/views/oj.py), 프롬프트 종료 조건(problem/llm_hint.py),
# 집계(problem/views/ai_hint_stats.py)가 이 값을 참조한다.
#
# 다만 이 값만 바꾸면 기능이 어긋난다. 아래 두 곳은 아직 5가 글로 박혀 있다.
#   - llm_hint.SYSTEM_PROMPT: "exactly 5 levels" 와 [1단계]~[5단계] 목록
#   - frontend BottomDrag.vue: 학생에게 보이는 "n/5 회" 표시
# 숫자를 바꾸려면 위 두 곳도 함께 손봐야 한다.
HINT_LIMIT_PER_PROBLEM = 5
