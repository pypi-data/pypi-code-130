# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals


class Config(object):
    """Конфигурация журнала изменений."""

    #: Флаг, указывающий на неообходимость настройки подсистемы при запуске.
    skip_configure = False


# : Конфигурация подсистемы журналирования.
config = Config()
