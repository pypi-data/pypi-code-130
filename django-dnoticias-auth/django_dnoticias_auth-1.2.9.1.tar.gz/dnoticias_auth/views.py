import logging

from django.views.decorators.clickjacking import xframe_options_exempt
from django.http.response import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View, FormView
from django.shortcuts import render, redirect
from django import VERSION as DJANGO_VERSION
from django.urls import reverse_lazy
from django.conf import settings
from django.http import Http404

from mozilla_django_oidc.views import OIDCLogoutView, OIDCAuthenticationCallbackView

from .utils import delete_user_sessions, get_cookie_equivalency
from .forms import PasswordRecoveryDCSForm
from .redis import KeycloakSessionStorage

logger = logging.getLogger(__name__)


class SilentCheckSSOView(View):
    @method_decorator(xframe_options_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, "authentication/silent-check-sso.html", locals())


class DnoticiasOIDCLogoutView(OIDCLogoutView):
    http_method_names = ['get', 'post']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @property
    def redirect_url(self) -> str:
        """
        This function was created using the keycloak redirect URL as a LOGOUT_REDIRECT_URL
        /auth/realms/<realm>/protocol/openid-connect/logout?redirect_uri=<URL>

        If we provide a next value via POST, the redirect_uri will be that value.
        If we do not have a next value, the redirect_uri will be the base url.
        """
        logout_url = self.get_settings('LOGOUT_REDIRECT_URL', None)
        base_url = self.get_settings('BASE_URL', None)
        next_url = self.request.POST.get('next') or self.request.GET.get('next', '') or base_url

        if not logout_url:
            logout_url = ''
            logger.warning("No LOGOUT_REDIRECT_URL configured!")

        if not base_url:
            base_url = '/'
            logger.warning("No BASE_URL configured! Using / as default...")

        return logout_url + next_url if logout_url else base_url

    def post(self, request) -> HttpResponseRedirect:
        """
        This method extends the original oidc logout method and aditionally deletes
        the authentication cookies
        """
        keycloak_session_id = request.session.get("keycloak_session_id")
        cookies: dict = request.COOKIES

        if not keycloak_session_id:
            keycloak_session_id = cookies.get(get_cookie_equivalency("keycloak_session_id"))

        delete_user_sessions(keycloak_session_id)
        super().post(request)

        # Response is defined first because we need to delete the cookies before redirect
        response = HttpResponseRedirect(self.redirect_url)
        auth_cookies = get_cookie_equivalency(all_names=True)

        # This will delete any cookie with session_ (session_editions, session_comments, etc)
        [auth_cookies.update({cookie: cookie}) for cookie in cookies.keys() if "session_" in cookie]

        extra = {"domain": settings.AUTH_COOKIE_DOMAIN}

        # Fix compatibility issues with django < 2 (CMS)
        if DJANGO_VERSION[0] == 3:
            extra.update({"samesite": "Strict"})

        # Deletes ONLY the cookies that we need
        [response.delete_cookie(cookie, **extra) for _, cookie in auth_cookies.items()]

        return response


class DnoticiasOIDCAuthenticationCallbackView(OIDCAuthenticationCallbackView):

    def get(self, request):
        response = super().get(request)

        request.session["keycloak_session_id"] = request.GET.get("session_state")
        request.session.save()

        try:
            keycloak_session = KeycloakSessionStorage(
                request.session["keycloak_session_id"],
                request.session.session_key,
            )

            keycloak_session.create_or_update()
        except:
            logger.exception("Something wrong was happened :(")

        return response


class ApplicationDataView(View):
    template_name = "authentication/app-data.html"

    def get(self, request, *args, **kwargs):
        next_url = request.GET.get("next_url")

        access_token = request.session.get("oidc_access_token")
        refresh_token = request.session.get("oidc_refresh_token")
        access_token_expires_in = request.session.get("oidc_expires_in")
        refresh_token_expires_in = request.session.get("oidc_refresh_expires_in")

        return render(request, self.template_name, locals())


class PasswordRecoveryDCSFormView(FormView):
    template_name = "authentication/password-recovery.html"
    form_class = PasswordRecoveryDCSForm

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("migration_email"):
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        next_url = self.request.session.get("migration_next_url")
        login_url = reverse_lazy("oidc_authentication_init")
        return f"{login_url}?next_url={next_url}"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["password_recovery_url"] = \
            f"{settings.OIDC_RESET_PASSWORD_URL}?next={self.request.session.get('migration_next_url')}"
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["email"] = self.request.session.get("migration_email")
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
