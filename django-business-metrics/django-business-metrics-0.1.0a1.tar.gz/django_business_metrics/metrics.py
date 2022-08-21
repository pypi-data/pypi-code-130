from django.contrib.auth import get_user_model
from typing import Union


MetricOutput = Union[float, int, ]


def users() -> int:
    """Total user count"""
    User = get_user_model()
    return User.objects.count()


def active_users() -> int:
    """Active user count"""
    User = get_user_model()
    return User.objects.filter(is_active=True).count()
