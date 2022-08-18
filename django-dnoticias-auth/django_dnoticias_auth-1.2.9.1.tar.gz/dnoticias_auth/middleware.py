import logging
from re import Pattern
from requests.exceptions import HTTPError

from dnoticias_auth.redis import KeycloakSessionStorage
from django.utils.module_loading import import_string
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import BACKEND_SESSION_KEY
from django.utils.functional import cached_property
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import auth
from django.urls import reverse

import requests
from mozilla_django_oidc.middleware import SessionRefresh as SessionRefreshOIDC
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from mozilla_django_oidc.utils import absolutify
from dnoticias_services.authentication.keycloak import (
    get_user_keycloak_info,
)

from .utils import generate_oidc_cookies, get_cookie_equivalency, get_cookie_configuration
from .backends import ExtraClaimsOIDCAuthenticationBackend

User = get_user_model()
logger = logging.getLogger(__name__)


class BaseAuthMiddleware:
    @cached_property
    def exempt_url_patterns(self):
        exempt_patterns = set()

        for url_pattern in settings.AUTH_EXEMPT_URLS:
            if isinstance(url_pattern, Pattern):
                exempt_patterns.add(url_pattern)

        return exempt_patterns

    @cached_property
    def exempt_session_url_patterns(self):
        exempt_patterns = set()
        patterns = getattr(settings, "SESSION_CHECK_EXEMPT_URLS", [])

        for url_pattern in patterns:
            if isinstance(url_pattern, Pattern):
                exempt_patterns.add(url_pattern)

        return exempt_patterns 

    def _is_processable(self, request):
        pass


class SessionRefresh(SessionRefreshOIDC):
    def is_refreshable_url(self, request):
        """Takes a request and returns whether it triggers a refresh examination

        :arg HttpRequest request:

        :returns: boolean

        """
        # Do not attempt to refresh the session if the OIDC backend is not used
        backend_session = request.session.get(BACKEND_SESSION_KEY)
        is_oidc_enabled = True
        if backend_session:
            auth_backend = import_string(backend_session)
            is_oidc_enabled = issubclass(auth_backend, OIDCAuthenticationBackend)

        return (
            request.method == 'GET' and
            not any(pat.match(request.path) for pat in self.exempt_url_patterns) and
            request.user.is_authenticated and
            is_oidc_enabled and
            request.path not in self.exempt_urls
        )


class LoginMiddleware(BaseAuthMiddleware, MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def _login_user(self, access_token, id_token, payload, request):
        """
        Ge get or create the user and then proceed to log in
        """
        UserModel = ExtraClaimsOIDCAuthenticationBackend()
        user = None

        try:
            user = UserModel.get_or_create_user(access_token, id_token, payload)
        except HTTPError as e:
            logger.debug("An HTTP error ocurred: {}".format(e))
        except:
            logger.exception("An exception has been ocurred on _login_user")

        if user:
            user.backend = "dnoticias_auth.backends.ExtraClaimsOIDCAuthenticationBackend"
            auth.login(request, user)
            session_id = request.COOKIES.get(get_cookie_equivalency("keycloak_session_id"))

            if session_id:
                keycloak_session = KeycloakSessionStorage(session_id, request.session.session_key)
                keycloak_session.create_or_update()

    def _is_processable(self, request):
        return (
            not any(pat.match(request.path) for pat in self.exempt_url_patterns) and
            not request.user.is_authenticated
        )

    def process_request(self, request):
        if not self._is_processable(request):
            return

        cookies = request.COOKIES
        session = request.session

        if not cookies.get(get_cookie_equivalency('oidc_access_token'), None):
            return
    
        # Setting the session items from cookies
        session['oidc_id_token_expiration'] = \
            float(cookies.get(get_cookie_equivalency('oidc_id_token_expiration'), 0))
        session['oidc_access_token'] = \
            cookies.get(get_cookie_equivalency('oidc_access_token'), None)
        session['oidc_id_token'] = \
            cookies.get(get_cookie_equivalency('oidc_id_token'), None)
        session['oidc_login_next'] = \
            cookies.get(get_cookie_equivalency('oidc_login_next'), None)

        # This condition avoids the exception 'OIDC callback'
        if not session.get('oidc_states'):
            session['oidc_states'] = \
                cookies.get(get_cookie_equivalency('oidc_states'), {})

        if not all([
            session['oidc_id_token_expiration'],
            session['oidc_access_token'],
            session['oidc_id_token']
        ]):
            return

        # Token payload that is used in OIDC to get (or refresh) an user token
        token_payload = {
            'client_id': settings.OIDC_RP_CLIENT_ID,
            'client_secret': settings.OIDC_RP_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': None,
            'redirect_uri': absolutify(
                request,
                ''
            ),
        }

        self._login_user(
            session['oidc_access_token'],
            session['oidc_id_token'],
            token_payload,
            request
        )

        return


class TokenMiddleware(BaseAuthMiddleware, MiddlewareMixin):
    """Just generates the cookie if the user is logged in"""
    def __init__(self, get_response):
        self.get_response = get_response

    def _is_processable(self, request):
        return (
            not any(pat.match(request.path) for pat in self.exempt_url_patterns) and
            request.user.is_authenticated
        )

    def _can_check_dcs_session(self, request):
        """Check if the request requires to check the sessionid on dcs
        
        :param request: httpRequest
        ...
        :return: True if the request if processable and the function proceeds to check the ssid
        """
        return (
            not any(pat.match(request.path) for pat in self.exempt_url_patterns)\
            and not any(pat.match(request.path) for pat in self.exempt_session_url_patterns)\
            and not request.user.is_authenticated\
            and request.COOKIES.get("sessionid")
        )

    def __is_user_migrated(self, email: str) -> bool:
        """Check on keycloak if the user has been migrated
        :param email: The user email that we will verify if has been migrated
        ...
        :return: True if the user has been migrated
        """
        user_info = get_user_keycloak_info(email)
        return bool(user_info.get("attributes", {}).get("user_migrated", False))

    def check_dcs_cookies(self, request, http_response):
        """Check the dcs cookies and redirects to password reset view
        
        :param request: httpRequest
        :param http_response: httpResponse
        ...
        :return: httpResponse
        """
        cookies = request.COOKIES
        session_id = cookies.get("sessionid")
        has_dcs_session_api = getattr(settings, "DCS_SESSION_MIGRATE_API_URL", False)

        # If we dont have a session_id cookie, we just return the initial response
        if not session_id or not has_dcs_session_api:
            return http_response

        dcs_session_api = getattr(settings, "DCS_SESSION_MIGRATE_API_URL")
        # We ask to the DCS the email associated to that session_id. This returns an email if the
        # sessionid is not anon, the user does not have @dnoticias.pt in his email and is not part
        # of the staff or superuser.
        response = requests.post(dcs_session_api, {"session_id": session_id})
        body = response.json()
        logger.debug("[DCS Session] Returned %s", body)

        if response.status_code == 200:
            if not body.get("error"):
                # Gets the email from body
                email = body.get("email")

                if not self.__is_user_migrated(email):
                    # We make an HttpResponseRedirect to the change password view
                    http_response = HttpResponseRedirect(reverse("password-recovery"))

                    request.session["migration_email"] = email
                    request.session["migration_next_url"] = request.build_absolute_uri()
                    request.session.save()

                # Deletes the sessionid cookie
                extra_data = get_cookie_configuration()
                extra_data.pop('expires')
                extra_data.pop('secure')
                extra_data.pop('httponly')
                http_response.delete_cookie('sessionid', **extra_data)

        return http_response

    def process_response(self, request, response):
        if self._can_check_dcs_session(request):
            response = self.check_dcs_cookies(request, response)

        # If the user is logged in then we set the cookies, else we delete it
        if self._is_processable(request):
            response = generate_oidc_cookies(request.session, response)

        return response
