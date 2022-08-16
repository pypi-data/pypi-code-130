from .emitters import Emitter
from .holidays import *


def for_locale(locale_id):
    locale_class = next(iter([cls for cls in Locale.plugins if cls.locale == locale_id]), None)
    if not locale_class:
        raise NotImplementedError
    else:
        return locale_class()


def for_country(country_id):
    country_class = next(iter([cls for cls in Country.plugins if cls.locale == country_id]), None)
    if not country_class:
        raise NotImplementedError
    else:
        return country_class()
