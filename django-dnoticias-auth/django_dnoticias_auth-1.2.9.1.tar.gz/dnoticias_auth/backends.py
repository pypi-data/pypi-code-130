import logging
import time
from datetime import datetime

from django.core.exceptions import SuspiciousOperation
from django.urls import reverse

from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from mozilla_django_oidc.utils import absolutify

logger = logging.getLogger(__name__)

class ExtraClaimsOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        """Return object for a newly created user account."""
        
        email = claims.get('email')
        first_name = claims.get("given_name", "")
        last_name = claims.get("family_name", "")
        is_staff = claims.get("is_staff", False)
        is_active = claims.get("is_active", True)
        is_superuser = claims.get("is_superuser", False)

        username = self.get_username(claims)

        return self.UserModel.objects.create_user(username, email, first_name=first_name, last_name=last_name, is_staff=is_staff, is_active=is_active, is_superuser=is_superuser)
    
    def update_user(self, user, claims):
        has_changes = False

        email = claims.get('email')
        first_name = claims.get("given_name", "")
        last_name = claims.get("family_name", "")
        is_staff = claims.get("is_staff", False)
        is_active = claims.get("is_active", True)
        is_superuser = claims.get("is_superuser", False)

        if user.first_name != first_name:
            user.first_name = first_name
            has_changes = True
        
        if user.last_name != last_name:
            user.last_name = last_name
            has_changes = True
        
        if user.email != email:
            logger.info("Updating user email...")
            user.email = email
            has_changes = True
        
        if user.is_staff != is_staff:
            logger.info("Updating user staff status...")
            user.is_staff = is_staff
            has_changes = True
        
        if user.is_active != is_active:
            logger.info("Updating user active status...")
            user.is_active = is_active
            has_changes = True
        
        if user.is_superuser != is_superuser:
            logger.info("Updating super user status...")
            user.is_superuser = is_superuser
            has_changes = True
        
        if has_changes:
            user.save()

        return user

    def __get_isoformat_from_timestamp(self, timestamp: int) -> str:
        timestamp += time.time()
        return datetime.fromtimestamp(timestamp).isoformat()

    def authenticate(self, request, **kwargs):
        """Authenticates a user based on the OIDC code flow."""

        self.request = request
        if not self.request:
            return None

        state = self.request.GET.get('state')
        code = self.request.GET.get('code')
        nonce = kwargs.pop('nonce', None)

        if not code or not state:
            return None

        reverse_url = self.get_settings('OIDC_AUTHENTICATION_CALLBACK_URL',
                                        'oidc_authentication_callback')

        token_payload = {
            'client_id': self.OIDC_RP_CLIENT_ID,
            'client_secret': self.OIDC_RP_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': absolutify(
                self.request,
                reverse(reverse_url)
            ),
        }

        # Get the token
        token_info = self.get_token(token_payload)
        id_token = token_info.get('id_token')
        access_token = token_info.get('access_token')
        refresh_token = token_info.get('refresh_token')
        expires_in = self.__get_isoformat_from_timestamp(token_info.get('expires_in'))
        refresh_expires_in = \
            self.__get_isoformat_from_timestamp(token_info.get('refresh_expires_in'))

        # Validate the token
        payload = self.verify_token(id_token, nonce=nonce)

        if payload:
            self.store_tokens(access_token, id_token, refresh_token, expires_in, refresh_expires_in)
            try:
                return self.get_or_create_user(access_token, id_token, payload)
            except SuspiciousOperation as exc:
                logger.warning('failed to get or create user: %s', exc)
                return None

        return None

    def store_tokens(self, access_token, id_token, refresh_token, expires_in, refresh_expires_in):
        """Store OIDC tokens."""
        session = self.request.session

        if self.get_settings('OIDC_STORE_ACCESS_TOKEN', False):
            session['oidc_access_token'] = access_token

        if self.get_settings('OIDC_STORE_ID_TOKEN', False):
            session['oidc_id_token'] = id_token

        if self.get_settings('OIDC_STORE_ACCESS_TOKEN_EXPIRATION', False):
            session['oidc_expires_in'] = expires_in

        if self.get_settings('OIDC_STORE_REFRESH_TOKEN_EXPIRATION', False):
            session['oidc_refresh_expires_in'] = refresh_expires_in

        if self.get_settings('OIDC_STORE_REFRESH_TOKEN', False):
            session['oidc_refresh_token'] = refresh_token
