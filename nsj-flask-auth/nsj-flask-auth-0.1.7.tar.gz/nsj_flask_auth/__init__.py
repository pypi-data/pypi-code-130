__version__ = "0.1.7"

from functools import wraps
import requests

from flask import request, abort, jsonify, g

from nsj_flask_auth.caching import Caching

from nsj_flask_auth.exceptions.unauthorized import Unauthorized
from nsj_flask_auth.exceptions.missing_auth_header import MissingAuthorizationHeader


class Auth:
    """Esta classe é responsável por disponibilizar um fluxo básico de autenticação através
    dos métodos decoradores requires_api_key, requires_access_token e requires_api_or_access_token.

    Para seu funcionamento mínimo é necessário que você defina os seguintes parâmetros:

    diretorio_base_uri: raiz da url do diretório.

    profile_uri: url do endpoint que retorna o perfil do usuário.

    diretorio_api_key: chave de acesso da sua aplicação.

    Recomenda-se instanciar a classe em um arquivo próprio e importar sua instância a partir dele.

    Caso tenha sido implementado um serviço de caching na aplicação é possível fornecer uma
    instância do objeto como parametro de inicialização. Até o momento este recurso só foi
    validado com instancias do módulo flask_caching.

    A inicialização também permite configurar as permissões de acesso necessárias
    (user_internal_permissions, user_tenant_permissions, app_required_permissions). Porém caso
    seja configurado na sua iniciliazação, não será possível utilizar o método decorador com
    permissões menores do que a configurada.
    """

    _cache = None

    def __init__(
        self,
        diretorio_base_uri: str = None,
        profile_uri: str = None,
        diretorio_api_key: str = None,
        api_key_header: str = "X-API-Key",
        access_token_header: str = "Authorization",
        user_internal_permissions: list = [],
        user_tenant_permissions: list = [],
        app_required_permissions: list = [],
        caching_service=None,
    ):
        self._diretorio_base_uri = diretorio_base_uri
        self._profile_uri = profile_uri
        self._diretorio_api_key = diretorio_api_key
        self._api_key_header = api_key_header
        self._access_token_header = access_token_header
        self._user_internal_permissions = user_internal_permissions
        self._user_tenant_permissions = user_tenant_permissions
        self._app_required_permissions = app_required_permissions
        if caching_service:
            self._cache = Caching(caching_service)

    def _verify_api_key(self, app_required_permissions: list = None):
        api_key = request.headers.get(self._api_key_header)

        if not api_key:
            raise MissingAuthorizationHeader(f"Missing {self._api_key_header} header")

        app_profile = self._get_app_profile(api_key)

        if app_profile["tipo"] == "sistema":
            g.user = app_profile["sistema"]["nome"]
            return

        raise Unauthorized("Somente api-keys de sistema são válidas")

    def _verify_access_token(
        self,
        user_internal_permissions: list = None,
        user_tenant_permissions: list = None,
    ):

        access_token = request.headers.get(self._access_token_header)

        if not access_token:
            raise MissingAuthorizationHeader(
                f"Missing {self._access_token_header} header"
            )

        user_profile = self._get_user_profile(access_token)

        email = user_profile.get("email")

        if not email:
            raise Unauthorized("O token do usuário não é válido")

        if user_internal_permissions:
            self._verify_user_permissions(user_internal_permissions, email)
            return

        if self._user_internal_permissions:
            self._verify_user_permissions(self._user_internal_permissions, email)
            return

        g.user = email

        return

    def _verify_user_permissions(self, user_internal_permissions: list, email: str):

        user_profile = None

        if self._cache:
            user_profile = self._cache.get(email)

        if not user_profile:
            url = self._diretorio_base_uri + "/profile/" + email
            headers = {"apikey": self._diretorio_api_key}
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise Unauthorized("A api-key do sistema não é válida")

            user_profile = response.json()

        if self._cache:
            self._cache.set(email, user_profile)

        if list(
            set(user_profile.get("permissao", [])) & set(user_internal_permissions)
        ):
            return

        raise Unauthorized("O usuário não possui permissão para acessar este recurso.")

    def _verify_api_key_or_access_token(
        self,
        app_required_permissions: list = None,
        user_internal_permissions: list = None,
        user_tenant_permissions: list = None,
    ):
        message = ""

        try:
            self._verify_api_key(app_required_permissions)
            return
        except MissingAuthorizationHeader:
            pass
        except Unauthorized as e:
            message = e
            pass

        try:
            self._verify_access_token(user_internal_permissions)
            return
        except MissingAuthorizationHeader:
            if not message:
                message = "Missing Authorization header"

        raise Unauthorized(message)

    def _get_user_profile(self, access_token):

        if self._cache:
            user_profile = self._cache.get(access_token)
            if user_profile:
                return user_profile

        if "Bearer " not in access_token:
            access_token = "Bearer " + access_token

        headers = {"Authorization": access_token}
        response = requests.get(self._profile_uri, headers=headers)

        if response.status_code != 200:
            raise Unauthorized("O token do usuário não é válido")

        if self._cache:
            self._cache.set(access_token, response.json())

        return response.json()

    def _get_app_profile(self, api_key):

        if self._cache:
            app_profile = self._cache.get(api_key)
            if app_profile:
                return app_profile

        data = f"apikey={api_key}"

        headers = {
            "apikey": self._diretorio_api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        url = self._diretorio_base_uri + "/validate"

        response = requests.post(url, data=data, headers=headers)

        if response.status_code != 200:
            raise Unauthorized("A api-key do sistema não é válida")

        if self._cache:
            self._cache.set(api_key, response.json())

        return response.json()

    def requires_api_key(self, app_required_permissions: list = None):
        """Decorador que garante o envio de uma api-key válida. Caso não seja enviada ou seja
        enviado uma api-key inválida, a chamada será automaticamente abortada. A parametrização
        da mensagem de erro ainda não está disponível. O decorador também aceita como parametro
        uma lista de permissões que o sistema deve ter para acessar o recurso. Esta lista trabalha
        em adição a lista fornceida na inicialização da classe.
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    self._verify_api_key(app_required_permissions)
                    return func(*args, **kwargs)
                except Unauthorized as e:
                    abort(jsonify({"Erro": f"{e}"}), 401)

            return wrapper

        return decorator

    def requires_access_token(
        self,
        user_internal_permissions: list = None,
        user_tenant_permissions: list = None,
    ):
        """Decorador que garante o envio de um access token válido. Caso não seja enviadu ou seja
        enviado um access token inválido, a chamada será automaticamente abortada. A parametrização
        da mensagem de erro ainda não está disponível. O decorador também aceita como parametro
        uma lista de permissões internas que o usuário deve ter para acessar o recurso.
        Esta lista trabalha em adição a lista fornceida na inicialização da classe. Também é
        possível fornecer uma lista de permissões por tenant, porém esta funcionalidade ainda
        não está disponível.
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    self._verify_access_token(
                        user_internal_permissions, user_tenant_permissions
                    )
                    return func(*args, **kwargs)
                except Unauthorized as e:
                    abort(jsonify({"Erro": f"{e}"}), 401)

            return wrapper

        return decorator

    def requires_api_key_or_access_token(
        self,
        app_required_permissions: list = None,
        user_internal_permissions: list = None,
        user_tenant_permissions: list = None,
    ):
        """Fluxo que implementa os decoradores requires_access_token e requires_api_key.
        Neste fluxo, caso seja enviado na mesma requisição um access token e uma api key,
        primeiro é validado o api-key e se for válido, o access token é ignorado.
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    self._verify_api_key_or_access_token(
                        app_required_permissions,
                        user_internal_permissions,
                        user_tenant_permissions,
                    )
                    return func(*args, **kwargs)
                except Unauthorized as e:
                    abort(jsonify({"Erro": f"{e}"}), 401)

            return wrapper

        return decorator
