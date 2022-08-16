import json
from urllib.parse import urlencode

from django import template
from django.shortcuts import reverse

# The JSONEncoder from DRF handles quite a few types, so we default to that
# if available and if not fallback to the Django one which still handles some
# extra types
try:
    from rest_framework.utils.encoders import JSONEncoder
except ImportError:
    from django.core.serializers.json import DjangoJSONEncoder as JSONEncoder


register = template.Library()


@register.simple_tag(takes_context=True)
def qs(context, *args, **kwargs):
    """
    Query string handler for paginators and filters

    Assuming we have a query string like ?page=1&search=foo, there are
    several cases in which we want to replace only the page key, while leaving
    the rest alone. This tag allows us to replace individual values (like the
    current page) while carrying over other values (like a search string)

    Example:
    <a href="?{% qs 'page' page_obj.next_page_number %}">
    <a href="?{% qs foo=bar %}">
    """
    qs = context["request"].GET.copy()
    # We special case when args are passed, because the first arg may
    # be the name of a key we want to replace. If an item is pased as
    # args, we'll add it to our kwargs so the rest of our code is simple
    if args:
        kwargs[args[0]] = args[1]
    for key in kwargs:
        if kwargs[key] is None:
            qs.pop(key, None)
        else:
            qs[key] = kwargs[key]
    return urlencode(qs)


@register.filter(name="prettyjson")
def prettyjson(value):
    if isinstance(value, str):
        value = json.loads(value)
    return json.dumps(
        value,
        indent=2,
        sort_keys=True,
        cls=JSONEncoder,
    )


@register.simple_tag(takes_context=True)
def fullurl(context, viewname, *args, **kwargs):
    return context["request"].build_absolute_uri(
        reverse(viewname, args=args, kwargs=kwargs)
    )
