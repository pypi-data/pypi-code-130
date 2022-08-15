import os
import json
import base64
from dotenv import dotenv_values


class NodeEnv(object):
    def __init__(self):
        self._dotenv = dotenv_values()
        self.debug = self._get_env('SP_DEBUG', type_func=boolean, default=False)
        self.app_type = self._get_env('SP_APP_TYPE')
        self.user_id = self._get_env("SP_USER_ID", default='dev_user_id')
        self.app_id = self._get_env("SP_APP_ID", default='dev_app_id')
        self.node_id = self._get_env("SP_NODE_ID", default='dev_node_id')
        self.api_host = self._get_env("SP_API_HOST")
        self.api_host_tls = self._get_env("SP_API_HOST_TLS", type_func=boolean, default=False)
        self.access_secret = self._get_env("SP_ACCESS_SECRET")
        self.user_id_header = self._get_env("SP_USER_ID_HEADER_FIELD", default='x-sp-user-id')
        self.user_signature_header = self._get_env("SP_USER_SIGNATURE_HEADER_FIELD", default='x-sp-signature')
        self.user_sign_version_header = self._get_env("SP_USER_SIGN_VERSION_HEADER_FIELD", default='x-sp-sign-version')

    def _get_env(self, name, type_func=None, default=None):
        value = os.environ.get(name)
        if not value:
            value = self._dotenv.get(name)
        if value is None and default is not None:
            value = default
        if type_func:
            value = type_func(value)

        return value

    def get_node_info(self):
        node_info = self._get_env("SP_NODE_INFO", type_func=b64decode, default='')
        return json.loads(node_info)

    def get_params(self):
        return self._get_env("SP_PARAM", type_func=b64decode, default='')

    def __str__(self):
        return 'debug: {}, type: {}, userid: {}, appid: {}, nodeid: {}'.format(
            self.debug, self.app_type, self.user_id, self.app_id, self.node_id)


def boolean(value):
    if isinstance(value, str):
        return value.lower() == 'true'
    elif isinstance(value, int):
        return bool(value)
    else:
        return False


def b64decode(value):
    return base64.b64decode(value).decode()
