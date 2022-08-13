import sys

from typing import (
    Optional,
    Tuple,
    Any,
    Type,
    TypeVar,
)

T = TypeVar("T")

import urllib.parse as urlparse    # noqa

text_type = str
string_types = (text_type,)    # type: Tuple[type]
number_types = (int, float)    # type: Tuple[type, type]
int_types = (int,)    # noqa
iteritems = lambda x: x.items()


def implements_str(x):
  # type: (T) -> T
  return x


def reraise(tp, value, tb=None):
  # type: (Optional[Type[BaseException]], Optional[BaseException], Optional[Any]) -> None
  assert value is not None
  if value.__traceback__ is not tb:
    raise value.with_traceback(tb)
  raise value


def with_metaclass(meta, *bases):
  # type: (Any, *Any) -> Any
  class MetaClass(type):

    def __new__(metacls, name, this_bases, d):
      # type: (Any, Any, Any, Any) -> Any
      return meta(name, bases, d)

  return type.__new__(MetaClass, "temporary_class", (), {})


def check_thread_support():
  # type: () -> None
  try:
    from uwsgi import opt    # type: ignore
  except ImportError:
    return

  # When `threads` is passed in as a uwsgi option,
  # `enable-threads` is implied on.
  if "threads" in opt:
    return

  if str(opt.get("enable-threads", "0")).lower() in ("false", "off", "no", "0"):
    from warnings import warn

    warn(
        Warning("We detected the use of uwsgi with disabled threads.  "
                "This will cause issues with the transport you are "
                "trying to use.  Please enable threading for uwsgi.  "
                '(Add the "enable-threads" flag).'))
