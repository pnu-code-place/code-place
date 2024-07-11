from django.db.models import Choices


class Difficulty(Choices):
    VERYLOW = "VeryLow"
    LOW = "Low"
    MID = "Mid"
    HIGH = "High"
    VERYHIGH = "VeryHigh"


LINK_NOTICE_SCRAPING_URL = "https://swedu.pusan.ac.kr/swedu/31630/subview.do"
LINK_NOTICE_LIMIT = 5

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