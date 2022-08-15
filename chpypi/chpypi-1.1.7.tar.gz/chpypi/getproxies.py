import requests
from chpypi import settings


class PROXIES:

    def __init__(self):
        ...

    @classmethod
    def get_shenlong_proxies(cls):
        '''神龙代理'''
        for _ in range(3):
            try:
                rsp = requests.get(url="http://api.shenlongip.com/ip?key="+settings.proxiesKey+"&pattern=txt&count=1&protocol=2",timeout=5)
                code = rsp.status_code
                r = rsp.text.strip()
                if "白名单" in r:
                    return {"code":400,"message":r,"proxies":""}
                elif code == 200:
                    proxies = {"https": "http://" + r,
                               "http": "http://" + r}
                    return {"code":200,"message":"success","proxies":proxies}
                else:
                    return {"code":401,"message":r,"proxies":""}
            except:
                return {"code": 500,
                        "message": 'failed to Obtain ip,try again',
                        "proxies": ""}

    @classmethod
    def get_aby_proxies(cls):
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": settings.proxyHost,
            "port": settings.proxyPort,
            "user": settings.proxyUser,
            "pass": settings.proxyPass,
        }
        proxies ={
            "http": proxyMeta,
            "https": proxyMeta,
        }
        return proxies


if __name__ == '__main__':
    ...
