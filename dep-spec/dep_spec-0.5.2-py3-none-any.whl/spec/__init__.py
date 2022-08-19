"""Service specification."""

from spec import default, fn, types
from spec.types import Spec, exc_type
from spec.loader import load_spec

fn.load_env()

# TODO: добавить проверку использования той же версии спеки во всех либах
# 1. добавить исключение
# 2. проверять
#    -> подключаемые модули
#    -> либе сервиса
