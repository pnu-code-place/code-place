import logging
import time

from django.contrib.sessions.backends.cache import SessionStore as CacheSessionStore
from django.contrib.sessions.backends.base import CreateError, UpdateError
from django.contrib.sessions.backends.cached_db import SessionStore as CachedDatabaseSessionStore
from django.contrib.sessions.backends.db import SessionStore as DatabaseSessionStore

logger = logging.getLogger(__name__)

CACHE_ERROR_LOG_INTERVAL_SECONDS = 30
_last_cache_error_log_at = {}


def _log_cache_error(action):
    now = time.monotonic()
    last_logged_at = _last_cache_error_log_at.get(action, 0)
    if now - last_logged_at < CACHE_ERROR_LOG_INTERVAL_SECONDS:
        return
    _last_cache_error_log_at[action] = now
    logger.warning("Failed to %s session cache; using the database", action, exc_info=True)


class SessionStore(CachedDatabaseSessionStore):
    """Database-backed sessions with Redis as a best-effort read cache.

    Keep the old cache-only backend's key prefix so active sessions can be
    loaded from Redis and persisted to the database without forcing logout
    during deployment.
    """

    cache_key_prefix = CacheSessionStore.cache_key_prefix

    def load(self):
        try:
            data = self._cache.get(self.cache_key)
        except Exception:
            _log_cache_error("read")
            data = None

        if data is not None:
            return data

        database_session = self._get_session_from_db()
        if database_session is None:
            return {}

        data = self.decode(database_session.session_data)
        try:
            self._cache.set(
                self.cache_key,
                data,
                self.get_expiry_age(expiry=database_session.expire_date),
            )
        except Exception:
            _log_cache_error("write")
        return data

    def exists(self, session_key):
        if not session_key:
            return False
        try:
            if self._cache.has_key(self.cache_key_prefix + session_key):
                return True
        except Exception:
            _log_cache_error("check")
        return DatabaseSessionStore.exists(self, session_key)

    def save(self, must_create=False):
        if self.session_key is None:
            self.create()
            return

        try:
            DatabaseSessionStore.save(self, must_create=must_create)
        except UpdateError:
            # A session created by the previous cache-only backend has no DB
            # row yet. Insert it, while tolerating another request winning the
            # same migration race.
            try:
                DatabaseSessionStore.save(self, must_create=True)
            except CreateError:
                DatabaseSessionStore.save(self, must_create=False)
        try:
            self._cache.set(self.cache_key, self._session, self.get_expiry_age())
        except Exception:
            _log_cache_error("write")

    def delete(self, session_key=None):
        if session_key is None:
            session_key = self.session_key
        if session_key is None:
            return

        DatabaseSessionStore.delete(self, session_key)
        try:
            self._cache.delete(self.cache_key_prefix + session_key)
        except Exception:
            _log_cache_error("delete")
