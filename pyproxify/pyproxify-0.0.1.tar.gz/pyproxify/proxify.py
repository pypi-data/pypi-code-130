import re, requests
from ua_headers import ua

def list2dict(x):
    return {
        "ip": x[0],
        "port": x[1],
        "country": {
            "code": x[2],
            "name": x[3]
        },
        "anonymity": x[4],
        "google": True if x[5] == "yes" else False,
        "https": True if x[6] == "yes" else False,
        "last_update": x[7] if len(x) > 7 else "", # My contribution, apparently this is the version problem since x[7] may not exist in new editions
        "url":
        "%s://%s:%s" % ("https" if x[6] == "yes" else "http", x[0], x[1])
    }


def make_request() -> list:
    headers = {
        'User-Agent': ua.windows(),
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Encoding': 'gzip',
        'Content-Type': 'text/html; charset=utf-8',
    }

    response = requests.get("https://free-proxy-list.net/", headers=headers).text

    return list(
        map(
            lambda x: tuple(re.findall(r"<td[^>]*>(.+?)</td>", x)
                            ),  # to this lambda
            re.findall(  # from this list
                r"<tr><td>[^<]*</td><td>[^<]*</td><td>[^<]*</td><td class='hm'>[^<]*</td><td>[^<]*</td><td class='hm'>[^<]*</td><td class='hx'>[^<]*</td><td class='hm'>[^<]*</td></tr>",
                response)))


def fetch(count=300, **kwargs) -> list:
    data = list(map(list2dict, make_request()))

    try:
        cc = kwargs["country"]
        data = filter(lambda x: x["country"]["code"] == cc, data)
    except KeyError:
        pass
    try:
        anonymity = kwargs["anonymity"]
        data = filter(lambda x: x["anonymity"] == anonymity, data)
    except KeyError:
        pass

    try:
        google = kwargs["google"]
        data = filter(lambda x: x["google"] == google, data)
        pass
    except KeyError:
        pass

    try:
        https = kwargs["https"]
        data = filter(lambda x: x["https"] == https, data)
        pass
    except KeyError:
        pass

    if count > 300:
        raise ValueError("Count can not exceed 300")

    return list(data)[:count]


