import json
import logging
import time

from redis.exceptions import LockError

from account.models import AdminType
from utils.cache import cache
from utils.constants import CacheKey, ContestRuleType

from .models import ACMContestRank, Contest, OIContestRank
from .serializers import ACMContestRankSerializer, OIContestRankSerializer

logger = logging.getLogger(__name__)

RANK_CACHE_FRESHNESS_SECONDS = 30
RANK_CACHE_RETENTION_SECONDS = 5 * 60
RANK_CACHE_LOCK_TIMEOUT_SECONDS = 10
RANK_CACHE_COLD_LOCK_WAIT_SECONDS = 0.5
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


def public_rank_cache_generation_key(contest_id):
    return f"{public_rank_cache_key(contest_id)}:generation"


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


def _decode_cached_public_rank(payload, contest_id):
    if payload is None:
        return None

    try:
        snapshot = json.loads(payload)
    except (TypeError, ValueError):
        logger.warning("Ignoring invalid contest %s rank cache payload", contest_id)
        return None

    # Cache entries created by the first version of this feature stored only
    # the list. Keep them available as stale data during a rolling deployment.
    if isinstance(snapshot, list):
        return 0, snapshot, 0

    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("data"), list):
        logger.warning("Ignoring invalid contest %s rank cache snapshot", contest_id)
        return None

    try:
        generation = int(snapshot["generation"])
    except (KeyError, TypeError, ValueError):
        logger.warning("Ignoring invalid contest %s rank cache generation", contest_id)
        return None
    try:
        refreshed_at = float(snapshot.get("refreshed_at", 0))
    except (TypeError, ValueError):
        refreshed_at = 0
    return generation, snapshot["data"], refreshed_at


def _snapshot_is_current(snapshot, generation, contest):
    if snapshot is None or snapshot[0] < generation:
        return False
    if not contest.real_time_rank:
        return True
    return time.time() - snapshot[2] < RANK_CACHE_FRESHNESS_SECONDS


def _get_public_rank_cache_state(contest_id):
    cache_key = public_rank_cache_key(contest_id)
    generation_key = public_rank_cache_generation_key(contest_id)
    try:
        cached_values = cache.get_many([cache_key, generation_key])
    except Exception:
        _log_cache_error("read", contest_id)
        return None, None

    snapshot = _decode_cached_public_rank(cached_values.get(cache_key), contest_id)
    try:
        generation = int(cached_values.get(generation_key, 0))
    except (TypeError, ValueError):
        logger.warning("Ignoring invalid contest %s rank cache generation marker", contest_id)
        return snapshot, None
    return snapshot, generation


def get_cached_public_rank(contest_id):
    snapshot, _generation = _get_public_rank_cache_state(contest_id)
    return snapshot[1] if snapshot is not None else None


def mark_public_rank_cache_stale(contest_id):
    try:
        return cache.incr(
            public_rank_cache_generation_key(contest_id),
            ignore_key_check=True,
        )
    except Exception:
        _log_cache_error("mark stale", contest_id)
        return None


def _refresh_public_rank_cache(contest_or_id, snapshot):
    contest_id = contest_or_id.id if isinstance(contest_or_id, Contest) else int(contest_or_id)
    cache_key = public_rank_cache_key(contest_id)
    stale_rank = snapshot[1] if snapshot is not None else None
    rank_data = stale_rank
    lock_wait = 0 if stale_rank is not None else RANK_CACHE_COLD_LOCK_WAIT_SECONDS

    try:
        with cache.lock(
            public_rank_cache_lock_key(contest_id),
            timeout=RANK_CACHE_LOCK_TIMEOUT_SECONDS,
            blocking_timeout=lock_wait,
        ):
            current_snapshot, current_generation = _get_public_rank_cache_state(contest_id)
            if current_generation is None:
                return stale_rank
            contest = contest_or_id if isinstance(contest_or_id, Contest) else Contest.objects.get(id=contest_id)
            if _snapshot_is_current(current_snapshot, current_generation, contest):
                return current_snapshot[1]

            rank_data = serialize_public_rank(contest)
            try:
                timeout = RANK_CACHE_RETENTION_SECONDS if contest.real_time_rank else None
                payload = {
                    "generation": current_generation,
                    "refreshed_at": time.time(),
                    "data": rank_data,
                }
                cache.set(
                    cache_key,
                    json.dumps(payload, separators=(",", ":")),
                    timeout=timeout,
                )
            except Exception:
                # The DB snapshot is still valid for the current HTTP request.
                _log_cache_error("write", contest_id)
    except LockError:
        # Another request is already rebuilding. Keep serving the previous
        # snapshot instead of making every polling request wait or hit the DB.
        return rank_data
    except Exception:
        _log_cache_error("refresh", contest_id)

    return rank_data


def refresh_public_rank_cache(contest_or_id):
    contest = contest_or_id if isinstance(contest_or_id, Contest) else Contest.objects.get(id=int(contest_or_id))
    contest_id = contest.id
    snapshot, generation = _get_public_rank_cache_state(contest_id)
    if generation is None:
        return None
    if _snapshot_is_current(snapshot, generation, contest):
        return snapshot[1]
    return _refresh_public_rank_cache(contest, snapshot)


def get_public_rank(contest):
    snapshot, generation = _get_public_rank_cache_state(contest.id)
    if generation is None:
        return None
    if _snapshot_is_current(snapshot, generation, contest):
        return snapshot[1]
    return _refresh_public_rank_cache(contest, snapshot)
