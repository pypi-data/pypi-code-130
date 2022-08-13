from django import template
import re

register = template.Library()  # 不用传参

def line_feed(string, num):
    s = string
    for i in range(len(s)):
        if not i % num and i != 0:
            s = s[:i] + "<br/>" + s[i:]
    return s

@register.filter
def getobjattr(obj, attr):
    return getattr(obj, attr, None)

@register.filter
def getkey(dic, key):
    regex = re.compile('http[s]?://.+')
    result = dic.get(key, None)
    if regex.search(str(result)):
        return f'<a href="{result}" target="_blank">{line_feed(str(result), 30)}</a>'
    if type(result) == list:
        return ' '.join(str(result))
    return result

@register.simple_tag
def get_all_attrs(dicts):
    if type(dicts) == list:
        try:
            return dicts[0].keys()
        except IndexError:
            return []
    elif type(dicts) == dict:
        return dicts.keys()
    else:
        return []