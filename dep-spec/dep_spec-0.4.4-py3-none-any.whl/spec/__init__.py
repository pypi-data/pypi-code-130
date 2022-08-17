"""Service specification."""

from spec import default, fn, types
from spec.types import Spec, exc_type
from spec.loader import load_spec


fn.load_env()

# TODO иерархия исключений

# TODO статус плагина в случае исключения
# TODO [счетчик] список ошибок плагина
