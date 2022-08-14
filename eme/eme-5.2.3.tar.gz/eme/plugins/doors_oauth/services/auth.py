import requests
from authlib.integrations.requests_client import OAuth2Auth
from authlib.oauth2.rfc6749 import TokenMixin
from authlib.oauth2.rfc6750 import BearerTokenValidator
from authlib.integrations.flask_oauth2 import ResourceProtector
from flask_login import LoginManager
#from eme.websocket import RouteForbiddenError
# todo: import exceptions without import entire WS eme
from werkzeug.utils import redirect

user_entity = None
user_repo = None
require_oauth = ResourceProtector()
login_manager = LoginManager()

conf: dict
allowed_noauth = set()
_validator: BearerTokenValidator


class DoorsCachedToken(TokenMixin):

    def __init__(self, access_token, user, expires_in=None, issued_at=None):
        self.access_token = access_token
        self.user = user
        self.expires_in = expires_in
        self.issued_at = issued_at

    def get_client_id(self):
        return conf['client_id']

    def get_scope(self):
        return conf['scope']

    def get_expires_in(self):
        return self.expires_in

    def get_expires_at(self):
        if self.issued_at is None or self.expires_in is None:
            # bugfix for records that have no expiry
            return 0

        return self.expires_in + self.issued_at


class DoorsTokenValidator(BearerTokenValidator):

    def authenticate_token(self, token_string):
        # tokens are cached in a user table
        user = user_repo.find_by_token(token_string)

        if user is not None:
            return DoorsCachedToken(token_string, user)

        return None

        # q = session.query(token_model)
        # return q.filter_by(access_token=token_string).first()

    def request_invalid(self, request):
        return False

    def token_revoked(self, token):
        return False


def init(app, c, entitycls, entityrepo):
    global login_manager, conf, user_repo, user_entity
    conf = c
    user_entity = entitycls
    user_repo = entityrepo

    app.config["SECRET_KEY"] = conf.get("secret_key")

    login_manager.init_app(app)
    login_manager.login_view = 'doors.Users:get_auth'

    # oauth protector
    require_oauth.register_token_validator(DoorsTokenValidator())


def init_ws(app, c, repo):
    global _validator, conf, user_repo
    conf = c
    user_repo = repo

    _validator = DoorsTokenValidator()


@login_manager.user_loader
def load_user(uid):
    if uid is None or uid == 'None':
        return None

    return user_repo.get(uid)


def get_authorize_url():
    return conf['doors_url'] + conf['doors_auth_endpoint'].format(conf['client_id'])


def fetch_token(code):
    doors_url = conf['doors_url']
    client_id = conf['client_id']
    client_secret = conf['client_secret']

    client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    r = requests.post(doors_url + '/oauth/token', verify=False, allow_redirects=False, data={
        'grant_type': 'authorization_code',
        'code': code,
        'scope': 'profile',

        # 'redirect_uri': 'https%3A%2F%2Fclient%2Eexample%2Ecom%2Fcb',
    }, auth=client_auth)

    if r.status_code != 200:
        return None

    access_token = r.json()['access_token']
    conf['access_token'] = access_token

    return access_token


def fetch_user(access_token=None):
    if access_token is None:
        access_token = conf['access_token']

    doors_url = conf['doors_url']

    token_auth = OAuth2Auth({
        'token_type': 'bearer',
        'access_token': access_token
    })

    r = requests.get(doors_url + "/oauth/me", headers={
        "access_token": access_token
    }, auth=token_auth)

    if r.status_code != 200:
        return None

    user = user_entity(**r.json())

    return user


def get_validator():
    return _validator


from functools import wraps

from flask import current_app, request
from flask_login import current_user
from flask_login.config import EXEMPT_METHODS


def is_admin(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.admin:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view


def login_forbidden(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif current_user.is_authenticated:
            return redirect('/')
        return func(*args, **kwargs)
    return decorated_view


def require_wsauth(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        #@todo: later: require profile too?

        if 'user' not in kwargs or not kwargs['user']:
            raise RouteForbiddenError()
        return func(*args, **kwargs)
    return decorated_view
