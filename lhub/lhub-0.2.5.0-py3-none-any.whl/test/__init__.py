import inspect
import lhub
import os
import logging

# ToDo Figure out how to resolve these warnings that show up when I run tests. They do not appear just from authenticating; only from tests invoking API calls.
# /Users/chad/code/python_env/python3_default/lib/python3.10/site-packages/urllib3/util/ssl_.py:273: DeprecationWarning: ssl.PROTOCOL_TLS is deprecated
#   context = SSLContext(ssl_version or PROTOCOL_TLS)
# /Users/chad/code/python_env/python3_default/lib/python3.10/site-packages/urllib3/connection.py:507: DeprecationWarning: ssl.match_hostname() is deprecated
#   match_hostname(cert, asserted_hostname)


# GENERAL environment variables
LOG_LEVEL = os.environ.get("LH_LOG_LEVEL", "").upper().strip() or None

logging.basicConfig(level=LOG_LEVEL)
log = logging.getLogger("lhub_tests")
if LOG_LEVEL:
    log.setLevel(LOG_LEVEL)


def print_test_ok(extra_string=None):
    print(f"OK - {inspect.stack()[1][3]}{extra_string or ''}")


class TestEnv:
    ENVIRONMENT_VARIABLES = [
        # For testing INVALID credentials, password auth
        "", "", "", ""

    ]

    def __init__(self):
        # For testing valid credentials, token auth
        self.INSTANCE_VALID_TK_HOSTNAME = self.__get_env_str("INSTANCE_VALID_TK_HOSTNAME")
        self.INSTANCE_VALID_TK_VERIFY_SSL = self.__get_env_str("INSTANCE_VALID_TK_VERIFY_SSL")
        self.INSTANCE_VALID_TK_TOKEN = self.__get_env_str("INSTANCE_VALID_TK_TOKEN")

        # For testing valid credentials, password auth
        self.INSTANCE_VALID_PW_HOSTNAME = self.__get_env_str("INSTANCE_VALID_PW_HOSTNAME")
        self.INSTANCE_VALID_PW_VERIFY_SSL = self.__get_env_bool("INSTANCE_VALID_PW_VERIFY_SSL", True)
        self.INSTANCE_VALID_PW_USERNAME = self.__get_env_str("INSTANCE_VALID_PW_USERNAME")
        self.INSTANCE_VALID_PW_PASSWORD = self.__get_env_str("INSTANCE_VALID_PW_PASSWORD")

        # For testing INVALID credentials, token auth
        self.INSTANCE_INVALID_TK_HOSTNAME = self.__get_env_str("INSTANCE_INVALID_TK_HOSTNAME")
        self.INSTANCE_INVALID_TK_VERIFY_SSL = self.__get_env_str("INSTANCE_INVALID_TK_VERIFY_SSL")
        self.INSTANCE_INVALID_TK_TOKEN = self.__get_env_str("INSTANCE_INVALID_TK_TOKEN")

        # For testing INVALID credentials, password auth
        self.INSTANCE_INVALID_PW_HOSTNAME = self.__get_env_str("INSTANCE_INVALID_PW_HOSTNAME")
        self.INSTANCE_INVALID_PW_VERIFY_SSL = self.__get_env_bool("INSTANCE_INVALID_PW_VERIFY_SSL", True)
        self.INSTANCE_INVALID_PW_USERNAME = self.__get_env_str("INSTANCE_INVALID_PW_USERNAME")
        self.INSTANCE_INVALID_PW_PASSWORD = self.__get_env_str("INSTANCE_INVALID_PW_PASSWORD")

        for v in self.ENVIRONMENT_VARIABLES:
            log.debug(f"Getting env: {v}")
            setattr(self, v, self.__get_env_str(v))
            if v.endswith('VERIFY_SSL'):
                setattr(self, v, getattr(self, v).lower() != "false")
        self.LOG_LEVEL = LOG_LEVEL

    @staticmethod
    def __get_env_str(env_name, default=None, trim_value=True):
        # _value = os.environ.get(env_name, default=default if default is not None else '')
        _value = os.environ.get(env_name, default='')
        if trim_value:
            _value = _value.strip()
        return _value or default

    def __get_env_bool(self, env_name, default=None):
        _value = self.__get_env_str(env_name, default='', trim_value=True).lower()
        if _value == "true":
            return True
        if _value == "false":
            return False
        if _value:
            raise ValueError(f"Variable \"{env_name}\" is not boolean: {_value}")
        return default


session_creds = TestEnv()

# Immediately establish an API token session with the credentials provided for testing with valid auth
token_session = lhub.LogicHub(
    hostname=session_creds.INSTANCE_VALID_TK_HOSTNAME,
    verify_ssl=session_creds.INSTANCE_VALID_TK_VERIFY_SSL,
    api_key=session_creds.INSTANCE_VALID_TK_TOKEN,
    # username=None,
    # password=None,
    # cache_seconds=None,
    # verify_api_auth=None,
    # default_timeout=None,
    # logger=None,
    log_level=session_creds.LOG_LEVEL
)

# Immediately establish a username/password session with the credentials provided for testing with valid auth
pw_session = lhub.LogicHub(
    hostname=session_creds.INSTANCE_VALID_PW_HOSTNAME,
    verify_ssl=session_creds.INSTANCE_VALID_PW_VERIFY_SSL,
    # api_key=None,
    username=session_creds.INSTANCE_VALID_PW_USERNAME,
    password=session_creds.INSTANCE_VALID_PW_PASSWORD,
    # cache_seconds=None,
    # verify_api_auth=None,
    # default_timeout=None,
    # logger=None,
    log_level=session_creds.LOG_LEVEL
)
