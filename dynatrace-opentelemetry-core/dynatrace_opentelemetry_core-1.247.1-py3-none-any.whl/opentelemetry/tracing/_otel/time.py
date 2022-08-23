import time

try:
    import dynatraceotel  # noqa: F401 pylint:disable=unused-import
except ImportError:
    try:
        from opentelemetry.util import _time
    except ImportError:
        _time = time
else:
    try:
        from dynatraceotel.util import _time
    except ImportError:
        _time = time

if hasattr(_time, "_time_ns"):
    _time_ns = _time._time_ns  # pylint: disable=protected-access
else:

    def _time_ns() -> int:
        return int(time.time() * 1e9)
