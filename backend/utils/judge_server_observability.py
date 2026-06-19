import json
import logging

from django.utils import timezone

from utils.cache import cache
from utils.constants import CacheKey

logger = logging.getLogger(__name__)


def sync_judge_server_snapshot(server, is_disabled=None, task_number=None):
    hostname = getattr(server, "hostname", None)
    if not hostname:
        return

    disabled = getattr(server, "is_disabled", False) if is_disabled is None else is_disabled
    if disabled:
        remove_judge_server_snapshot(hostname)
        return

    last_heartbeat = getattr(server, "last_heartbeat", None)
    if last_heartbeat is None:
        last_heartbeat_timestamp = 0
    else:
        last_heartbeat_timestamp = last_heartbeat.timestamp()

    payload = {
        "last_heartbeat_timestamp": last_heartbeat_timestamp,
        "task_number": int(task_number if task_number is not None else getattr(server, "task_number", 0) or 0),
    }
    try:
        cache.hset(CacheKey.judge_server_observability, hostname, json.dumps(payload))
    except Exception:
        logger.exception("Failed to sync judge-server observability snapshot")


def remove_judge_server_snapshot(hostname):
    if not hostname:
        return
    try:
        cache.hdel(CacheKey.judge_server_observability, hostname)
    except Exception:
        logger.exception("Failed to remove judge-server observability snapshot")


def increment_judge_server_task_snapshot(hostname, delta):
    if not hostname:
        return
    try:
        raw = cache.hget(CacheKey.judge_server_observability, hostname)
        if raw is None:
            return
        payload = _loads_snapshot(raw)
        payload["task_number"] = max(int(payload.get("task_number", 0)) + int(delta), 0)
        cache.hset(CacheKey.judge_server_observability, hostname, json.dumps(payload))
    except Exception:
        logger.exception("Failed to increment judge-server task snapshot")


def load_judge_server_snapshots():
    snapshots = []
    try:
        raw_snapshots = cache.hgetall(CacheKey.judge_server_observability) or {}
    except Exception:
        logger.exception("Failed to load judge-server observability snapshots")
        return None

    now_timestamp = timezone.now().timestamp()
    for raw_hostname, raw_payload in raw_snapshots.items():
        hostname = _decode(raw_hostname)
        payload = _loads_snapshot(raw_payload)
        last_heartbeat_timestamp = _float_or_zero(payload.get("last_heartbeat_timestamp"))
        heartbeat_age = max(now_timestamp - last_heartbeat_timestamp, 0) if last_heartbeat_timestamp else float("inf")
        snapshots.append({
            "hostname": hostname,
            "heartbeat_age": heartbeat_age,
            "available": 1 if heartbeat_age <= 6 else 0,
            "task_number": max(int(_float_or_zero(payload.get("task_number"))), 0),
        })
    return snapshots


def _loads_snapshot(raw):
    try:
        return json.loads(_decode(raw))
    except (TypeError, ValueError):
        return {}


def _decode(value):
    if isinstance(value, bytes):
        return value.decode()
    return str(value)


def _float_or_zero(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0
