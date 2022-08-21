# django-stardate-filter/stardate/templatetags/stardate.py

# System libraries
import json
import datetime

# Third-party libraries

# Django modules
from django import template
from django.template.defaultfilters import stringfilter
from django.conf import settings

# Django apps


#  Current app modules


register = template.Library()


@register.filter(name='stardate')
@stringfilter
def stardate(value):
    def leapyr(year):
        return 366 if year % 400 == 0 or (year % 4 == 0 and year % 100 != 0) else 365

    date_format = getattr(settings, 'STARDATE_FORMAT', '%Y-%m-%d %H:%M')
    t = datetime.datetime.strptime(value, date_format).timetuple()
    sd = getattr(settings, 'STARDATE', 96601.20)
    ed = getattr(settings, 'EARTHDATE', 2019)

    return format(((sd
                    + (1000 * (t.tm_year - ed)))
                    + ((1000 / ((leapyr(t.tm_year)) * 1440.0)) * (((t.tm_yday - 1.0) * 1440.0)
                    + (t.tm_hour * 60.0)
                    + t.tm_min))), '.2f')
