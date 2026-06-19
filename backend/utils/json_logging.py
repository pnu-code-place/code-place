import json
import logging
from datetime import datetime, timezone

from utils.observability_context import get_request_id
from utils.observability_tracing import get_current_trace_context


SENSITIVE_EXACT_FIELDS = {
    "authorization",
    "cookie",
    "password",
    "token",
    "secret",
    "code",
    "src",
}
SENSITIVE_SUBSTRINGS = {
    "authorization",
    "cookie",
    "password",
    "token",
    "secret",
    "source_code",
    "sourcecode",
    "spj_code",
    "src",
}


class CodePlaceJsonFormatter(logging.Formatter):

    def format(self, record):
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None) or get_request_id(),
        }
        payload.update(get_current_trace_context())
        for key in (
                "method",
                "path",
                "status_code",
                "duration_ms",
                "user_id",
                "remote_addr",
                "task_id",
                "task_name",
                "task_status",
                "submission_id",
                "retry_reason",
                "frontend_surface",
                "frontend_error_type",
                "frontend_message",
                "frontend_route",
                "frontend_release",
                "frontend_component",
                "frontend_info",
        ):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(self._redact(payload), ensure_ascii=False, default=str)

    def _redact(self, value):
        if isinstance(value, dict):
            return {
                key: "[REDACTED]" if self._is_sensitive_key(key) else self._redact(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self._redact(item) for item in value]
        return value

    @staticmethod
    def _is_sensitive_key(key):
        normalized = str(key).lower()
        return normalized in SENSITIVE_EXACT_FIELDS or any(field in normalized for field in SENSITIVE_SUBSTRINGS)
