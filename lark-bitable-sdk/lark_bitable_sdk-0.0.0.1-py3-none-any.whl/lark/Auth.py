import json
from typing import Optional

from lark import base_url, url_get_tenant_access_token
from utils.RestfulUtils import do_post
from vo.lark.LarkAuthTenantAccessTokenResponse import LarkAuthTenantAccessTokenResponse
from vo.lark.LarkBaseResponse import LarkBaseResponse


def AuthCheck(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, LarkBaseResponse) and result.code == 99991663:
            Auth().refresh_tenant_access_token()
            result = func(*args, **kwargs)
        return result

    return wrapper


class Auth:
    __instance__ = None
    __tenant_access_token__: Optional[str] = None
    __app_id__: Optional[str] = None
    __app_secret__: Optional[str] = None

    def __new__(cls, app_id=None, app_secret=None, *args, **kwargs):
        if not Auth.__instance__:
            Auth.__instance__ = object.__new__(cls)
            if app_id and app_secret:
                Auth.__app_id__ = app_id
                Auth.__app_secret__ = app_secret
            else:
                Auth.__app_id__, Auth.__app_secret__ = Auth.__loadProps__(Auth.__instance__)
        return Auth.__instance__

    def get_tenant_access_token(self, refresh=False):
        if not Auth.__tenant_access_token__ or refresh:
            Auth.__tenant_access_token__ = self.__get_tenant_access_token__(Auth.__app_id__,
                                                                            Auth.__app_secret__).tenant_access_token
        return Auth.__tenant_access_token__

    def __get_tenant_access_token__(self, app_id: str, app_secret: str) -> LarkAuthTenantAccessTokenResponse:
        return LarkAuthTenantAccessTokenResponse(
            **do_post(base_url + url_get_tenant_access_token, {"app_id": app_id, "app_secret": app_secret}))

    def __loadProps__(self):
        with open("../config.json", 'r') as load_f:
            result = json.load(load_f)
            return result['app_id'], result['app_secret']

    def get_headers(self, refresh=False):
        return {'Authorization': f'Bearer {self.get_tenant_access_token(refresh)}'}

    def refresh_tenant_access_token(self):
        self.get_tenant_access_token(True)
