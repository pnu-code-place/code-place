import json
import logging
import time

from account.models import AdminType
from utils.cache import cache
from utils.constants import CacheKey, ContestRuleType

from .models import ACMContestRank, Contest, OIContestRank
from .serializers import ACMContestRankSerializer, OIContestRankSerializer

logger = logging.getLogger(__name__)

RANK_CACHE_TIMEOUT_SECONDS = 30
RANK_CACHE_LOCK_TIMEOUT_SECONDS = 10
RANK_CACHE_LOCK_WAIT_SECONDS = 2
CACHE_ERROR_LOG_INTERVAL_SECONDS = 30
_last_cache_error_log_at = {}


def _log_cache_error(action, contest_id):
    now = time.monotonic()
    last_logged_at = _last_cache_error_log_at.get(action, 0)
    if now - last_logged_at < CACHE_ERROR_LOG_INTERVAL_SECONDS:
        return
    _last_cache_error_log_at[action] = now
    logger.warning("Failed to %s contest %s rank cache", action, contest_id, exc_info=True)


def public_rank_cache_key(contest_id):
    return f"{CacheKey.contest_rank_cache}:{contest_id}:public"


def public_rank_cache_lock_key(contest_id):
    return f"{public_rank_cache_key(contest_id)}:refresh-lock"


def get_contest_rank_queryset(contest):
    common_filter = {
        "contest": contest,
        "user__is_disabled": False,
        "user__admin_type__exact": AdminType.REGULAR_USER,
    }
    if contest.rule_type == ContestRuleType.ACM:
        return (
            ACMContestRank.objects.filter(**common_filter)
            .select_related("user", "user__userprofile")
            .order_by("-accepted_number", "total_time")
        )
    return (
        OIContestRank.objects.filter(**common_filter)
        .select_related("user", "user__userprofile")
        .order_by("-total_score")
    )


def serialize_public_rank(contest):
    serializer = OIContestRankSerializer if contest.rule_type == ContestRuleType.OI else ACMContestRankSerializer
    ranks = get_contest_rank_queryset(contest)
    return list(serializer(ranks, many=True).data)


def get_cached_public_rank(contest_id):
    try:
        payload = cache.get(public_rank_cache_key(contest_id))
    except Exception:
        _log_cache_error("read", contest_id)
        return None

    if payload is None:
        return None

    try:
        data = json.loads(payload)
    except (TypeError, ValueError):
        logger.warning("Ignoring invalid contest %s rank cache payload", contest_id)
        return None
    return data if isinstance(data, list) else None


def refresh_public_rank_cache(contest_or_id, force=False):
    contest_id = contest_or_id.id if isinstance(contest_or_id, Contest) else int(contest_or_id)
    cache_key = public_rank_cache_key(contest_id)
    rank_data = None

    try:
        with cache.lock(
            public_rank_cache_lock_key(contest_id),
            timeout=RANK_CACHE_LOCK_TIMEOUT_SECONDS,
            blocking_timeout=RANK_CACHE_LOCK_WAIT_SECONDS,
        ):
            if not force:
                cached_rank = get_cached_public_rank(contest_id)
                if cached_rank is not None:
                    return cached_rank
            # Delete first so a failed SET cannot leave an old snapshot active.
            cache.delete(cache_key)
            contest = contest_or_id if isinstance(contest_or_id, Contest) else Contest.objects.get(id=contest_id)
            rank_data = serialize_public_rank(contest)
            try:
                timeout = RANK_CACHE_TIMEOUT_SECONDS if contest.real_time_rank else None
                cache.set(
                    cache_key,
                    json.dumps(rank_data, separators=(",", ":")),
                    timeout=timeout,
                )
            except Exception:
                # The DB snapshot is still valid for the current HTTP request.
                _log_cache_error("write", contest_id)
    except Exception:
        _log_cache_error("refresh", contest_id)

    return rank_data


def get_public_rank(contest):
    rank_data = get_cached_public_rank(contest.id)
    if rank_data is not None:
        return rank_data
    return refresh_public_rank_cache(contest)
