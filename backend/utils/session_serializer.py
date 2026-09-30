import json
from datetime import datetime

DATETIME_MARKER = "__codeplace_datetime__"


class DateTimeJSONSerializer:

    @staticmethod
    def _default(value):
        if isinstance(value, datetime):
            return {DATETIME_MARKER: value.isoformat()}
        raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")

    @staticmethod
    def _object_hook(value):
        if set(value) == {DATETIME_MARKER}:
            return datetime.fromisoformat(value[DATETIME_MARKER])
        return value

    def dumps(self, value):
        return json.dumps(value, separators=(",", ":"), default=self._default).encode("latin-1")

    def loads(self, value):
        return json.loads(value.decode("latin-1"), object_hook=self._object_hook)
