import base64
import hashlib
import hmac
import requests
from urllib.parse import urlunsplit, urljoin
from spapp.exception import NodeEnvError, ApiError
from spapp.node_env import NodeEnv

env: NodeEnv


def setup_env(_env):
    global env
    env = _env


def api_host():
    if not env.api_host:
        raise NodeEnvError('empty api host')

    scheme = "https" if env.api_host_tls else "http"
    return urlunsplit((scheme, env.api_host, '', '', ''))


def api_url(path):
    return urljoin(api_host(), path)


def signature_v1(secret: str, user_id: str):
    if not secret:
        raise NodeEnvError('invalid SP_ACCESS_SECRET')

    h = hmac.new(secret.encode(), user_id.encode(), hashlib.sha1)
    digest = h.digest()
    return base64.b64encode(digest).decode()


def default_headers():
    if not env:
        raise NodeEnvError('call setup_env before api')

    return {
        env.user_id_header: env.user_id,
        env.user_signature_header: signature_v1(env.access_secret, env.user_id),
        env.user_sign_version_header: "v1"
    }


def session(auth=True):
    sess = requests.Session()
    if auth:
        sess.headers.update(default_headers())
    return sess


def get_graph():
    url = api_url(f'/app/graph/{env.app_id}')
    sess = session()
    rep = sess.get(url)
    rep.raise_for_status()
    result = rep.json()
    if not result.get("success", True):
        raise ApiError(f"api get graph failed: {result}")

    return result['data']
