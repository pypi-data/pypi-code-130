from abc import ABCMeta
from typing import TYPE_CHECKING

import six


if TYPE_CHECKING:
    from explicit.contrib.adapters.messaging.kafka import Adapter
    from explicit.messagebus import MessageBus


class IConfig(six.with_metaclass(ABCMeta, object)):
    """Конфигурация модуля управления доступом на основе ролей."""

    bus: 'MessageBus'
    """Внутренняя шина сервиса."""

    adapter: 'Adapter'
    """Адаптер к kafka"""


rbac_config: IConfig
