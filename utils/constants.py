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
    contest_rank_cache = "contest_rank_cache"
    website_config = "website_config"


class Difficulty(Choices):
    VERYLOW = "VeryLow"
    LOW = "Low"
    MID = "Mid"
    HIGH = "High"
    VERYHIGH = "VeryHigh"


CONTEST_PASSWORD_SESSION_KEY = "contest_password"


class ProblemField:
    strToInt = {
        'implementation': 0,
        'math': 1,
        'datastructure': 2,
        'search': 3,
        'sorting': 4,
    }
    intToStr = {
        0: 'implementation',
        1: 'math',
        2: 'datastructure',
        3: 'search',
        4: 'sorting',
    }


class ProblemScore:
    score = {
        'VeryLow': 20,      # VeryLow
        'Low': 40,      # Low
        'Mid': 160,      # Mid
        'High': 640,     # High
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
