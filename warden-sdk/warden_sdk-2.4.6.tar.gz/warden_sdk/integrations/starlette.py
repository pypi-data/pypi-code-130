from __future__ import absolute_import

import asyncio
import functools

from warden_sdk._compat import iteritems
from warden_sdk.hub import Hub, _should_send_default_pii
from warden_sdk.integrations import DidNotEnable, Integration
from warden_sdk.integrations._wsgi_common import (
    _is_json_content_type,
    request_body_within_bounds,
)
from warden_sdk.integrations.asgi import WardenAsgiMiddleware
from warden_sdk.tracing import (
    SOURCE_FOR_STYLE,
    TRANSACTION_SOURCE_ROUTE,
)
from warden_sdk.utils import (
    AnnotatedValue,
    capture_internal_exceptions,
    event_from_exception,
    transaction_from_function,
)
from warden_sdk import User

try:
  import starlette    # type: ignore
  from starlette.applications import Starlette    # type: ignore
  from starlette.datastructures import UploadFile    # type: ignore
  from starlette.middleware import Middleware    # type: ignore
  from starlette.middleware.authentication import (    # type: ignore
      AuthenticationMiddleware,)
  from starlette.requests import Request    # type: ignore
  from starlette.routing import Match    # type: ignore
  from starlette.types import ASGIApp, Receive, Scope, Send    # type: ignore
except ImportError:
  raise DidNotEnable("Starlette is not installed")

try:
  # Starlette 0.20
  from starlette.middleware.exceptions import ExceptionMiddleware    # type: ignore
except ImportError:
  # Startlette 0.19.1
  from starlette.exceptions import ExceptionMiddleware    # type: ignore

try:    # noqa
  import mangum    # type: ignore
except ImportError:
  raise DidNotEnable("mangum is not installed")

try:
  # Optional dependency of Starlette to parse form data.
  import multipart    # type: ignore # noqa: F401
except ImportError:
  multipart = None

_DEFAULT_TRANSACTION_NAME = "generic Starlette request"

TRANSACTION_STYLE_VALUES = ("endpoint", "url")


class StarletteIntegration(Integration):
  identifier = "starlette"

  transaction_style = ""

  def __init__(self, transaction_style="url"):
    # type: (str) -> None
    if transaction_style not in TRANSACTION_STYLE_VALUES:
      raise ValueError(
          "Invalid value for transaction_style: %s (must be in %s)" %
          (transaction_style, TRANSACTION_STYLE_VALUES))
    self.transaction_style = transaction_style

  @staticmethod
  def setup_once():
    # type: () -> None
    patch_middlewares()
    patch_asgi_app()
    patch_request_response()


def _enable_span_for_middleware(middleware_class):
  old_call = middleware_class.__call__

  async def _create_span_call(*args, **kwargs):
    hub = Hub.current
    integration = hub.get_integration(StarletteIntegration)
    if integration is not None:
      middleware_name = args[0].__class__.__name__
      with hub.start_span(op="starlette.middleware",
                          description=middleware_name) as middleware_span:
        middleware_span.set_tag("starlette.middleware_name", middleware_name)

        await old_call(*args, **kwargs)

    else:
      await old_call(*args, **kwargs)

  not_yet_patched = old_call.__name__ not in [
      "_create_span_call",
      "_warden_authenticationmiddleware_call",
      "_warden_exceptionmiddleware_call",
  ]

  if not_yet_patched:
    middleware_class.__call__ = _create_span_call

  return middleware_class


def _capture_exception(exception, handled=False):
  hub = Hub.current
  if hub.get_integration(StarletteIntegration) is None:
    return

  event, hint = event_from_exception(
      exception,
      client_options=hub.client.options if hub.client else None,
      mechanism={
          "type": StarletteIntegration.identifier,
          "handled": handled
      },
  )

  hub.capture_event(event, hint=hint)


def patch_exception_middleware(middleware_class):
  """
    Capture all exceptions in Starlette app and
    also extract user information.
    """
  old_middleware_init = middleware_class.__init__

  def _warden_middleware_init(self, *args, **kwargs):
    old_middleware_init(self, *args, **kwargs)

    # Patch existing exception handlers
    old_handlers = self._exception_handlers.copy()

    async def _warden_patched_exception_handler(self, *args, **kwargs):
      exp = args[0]

      is_http_server_error = hasattr(exp,
                                     "staus_code") and exp.status_code >= 500
      if is_http_server_error:
        _capture_exception(exp, handled=True)

      # Find a matching handler
      old_handler = None
      for cls in type(exp).__mro__:
        if cls in old_handlers:
          old_handler = old_handlers[cls]
          break

      if old_handler is None:
        return

      if _is_async_callable(old_handler):
        return await old_handler(self, *args, **kwargs)
      else:
        return old_handler(self, *args, **kwargs)

    for key in self._exception_handlers.keys():
      self._exception_handlers[key] = _warden_patched_exception_handler

  middleware_class.__init__ = _warden_middleware_init

  old_call = middleware_class.__call__

  async def _warden_exceptionmiddleware_call(self, scope, receive, send):
    # Also add the user (that was eventually set by be Authentication middle
    # that was called before this middleware). This is done because the authentication
    # middleware sets the user in the scope and then (in the same function)
    # calls this exception middelware. In case there is no exception (or no handler
    # for the type of exception occuring) then the exception bubbles up and setting the
    # user information into the warden scope is done in auth middleware and the
    # ASGI middleware will then send everything to Warden and this is fine.
    # But if there is an exception happening that the exception middleware here
    # has a handler for, it will send the exception directly to Warden, so we need
    # the user information right now.
    # This is why we do it here.
    _add_user_to_warden_scope(scope)
    await old_call(self, scope, receive, send)

  middleware_class.__call__ = _warden_exceptionmiddleware_call


def _add_user_to_warden_scope(scope):
  """
    Extracts user information from the ASGI scope and
    adds it to Warden's scope.
    """
  if "user" not in scope:
    return

  if not _should_send_default_pii():
    return

  hub = Hub.current
  if hub.get_integration(StarletteIntegration) is None:
    return

  with hub.configure_scope() as warden_scope:
    user_info = {}
    starlette_user = scope["user"]

    username = getattr(starlette_user, "username", None)
    if username:
      user_info.setdefault("username", starlette_user.username)

    user_id = getattr(starlette_user, "id", None)
    if user_id:
      user_info.setdefault("id", starlette_user.id)

    email = getattr(starlette_user, "email", None)
    if email:
      user_info.setdefault("email", starlette_user.email)

    warden_scope.user = user_info


def patch_authentication_middleware(middleware_class):
  """
    Add user information to Warden scope.
    """
  old_call = middleware_class.__call__

  async def _warden_authenticationmiddleware_call(self, scope, receive, send):

    await old_call(self, scope, receive, send)
    _add_user_to_warden_scope(scope)

  middleware_class.__call__ = _warden_authenticationmiddleware_call


def patch_middlewares():
  """
    Patches Starlettes `Middleware` class to record
    spans for every middleware invoked.
    """
  old_middleware_init = Middleware.__init__

  not_yet_patched = "_warden_middleware_init" not in str(old_middleware_init)

  if not_yet_patched:

    def _warden_middleware_init(self, cls, **options):
      span_enabled_cls = _enable_span_for_middleware(cls)
      old_middleware_init(self, span_enabled_cls, **options)

      if cls == AuthenticationMiddleware:
        patch_authentication_middleware(cls)

      if cls == ExceptionMiddleware:
        patch_exception_middleware(cls)

    Middleware.__init__ = _warden_middleware_init


def patch_asgi_app():
  """
    Instrument Starlette ASGI app using the WardenAsgiMiddleware.
    """
  old_app = Starlette.__call__

  async def _warden_patched_asgi_app(self, scope, receive, send):
    if Hub.current.get_integration(StarletteIntegration) is None:
      return await old_app(self, scope, receive, send)

    middleware = WardenAsgiMiddleware(
        lambda *a, **kw: old_app(self, *a, **kw),
        mechanism_type=StarletteIntegration.identifier,
    )
    middleware.__call__ = middleware._run_asgi3
    return await middleware(scope, receive, send)    # type: ignore

  Starlette.__call__ = _warden_patched_asgi_app


# This was vendored in from Starlette to support Starlette 0.19.1 because
# this function was only introduced in 0.20.x
def _is_async_callable(obj):
  while isinstance(obj, functools.partial):
    obj = obj.func

  return asyncio.iscoroutinefunction(obj) or (
      callable(obj) and asyncio.iscoroutinefunction(obj.__call__))


def patch_request_response():
  old_request_response = starlette.routing.request_response    # type: ignore

  def _warden_request_response(func):
    old_func = func

    is_coroutine = _is_async_callable(old_func)
    if is_coroutine:

      async def _warden_async_func(*args, **kwargs):
        hub = Hub.current
        integration = hub.get_integration(StarletteIntegration)
        if integration is None:
          return await old_func(*args, **kwargs)

        with hub.configure_scope() as warden_scope:
          request = args[0]
          extractor = StarletteRequestExtractor(request)
          info = await extractor.extract_request_info()

          def _make_request_event_processor(req, integration):

            def event_processor(event, hint):
              # Extract information from request
              request_info = event.get("request", {})
              if info:
                if "cookies" in info and _should_send_default_pii():
                  request_info["cookies"] = info["cookies"]
                if "data" in info:
                  request_info["data"] = info["data"]
              event["request"] = request_info

              _set_transaction_name_and_source(event,
                                               integration.transaction_style,
                                               req)

              return event

            return event_processor

        warden_scope._name = StarletteIntegration.identifier
        warden_scope.add_event_processor(
            _make_request_event_processor(request, integration))

        return await old_func(*args, **kwargs)

      func = _warden_async_func
    else:

      def _warden_sync_func(*args, **kwargs):
        hub = Hub.current
        integration = hub.get_integration(StarletteIntegration)
        if integration is None:
          return old_func(*args, **kwargs)

        with hub.configure_scope() as warden_scope:
          request = args[0]
          extractor = StarletteRequestExtractor(request)
          cookies = extractor.extract_cookies_from_request()

          def _make_request_event_processor(req, integration):

            def event_processor(event, hint):
              # Extract information from request
              request_info = event.get("request", {})
              if cookies:
                request_info["cookies"] = cookies

              event["request"] = request_info

              _set_transaction_name_and_source(event,
                                               integration.transaction_style,
                                               req)

              return event

            return event_processor

        warden_scope._name = StarletteIntegration.identifier
        warden_scope.add_event_processor(
            _make_request_event_processor(request, integration))

        return old_func(*args, **kwargs)

      func = _warden_sync_func

    return old_request_response(func)

  starlette.routing.request_response = _warden_request_response    # type: ignore


class StarletteRequestExtractor:
  """
    Extracts useful information from the Starlette request
    (like form data or cookies) and adds it to the Warden event.
    """

  request = None    # type: Request

  def __init__(self, request):
    self.request = request

  def extract_cookies_from_request(self):
    client = Hub.current.client
    if client is None:
      return None

    cookies = None
    if _should_send_default_pii():
      cookies = self.cookies()

    return cookies

  async def extract_request_info(self):
    client = Hub.current.client
    if client is None:
      return None

    data = None

    content_length = await self.content_length()
    request_info = {}

    with capture_internal_exceptions():
      aws_event = self.request.scope.get("aws.event")
      User.setup(aws_event)

      if _should_send_default_pii():
        request_info["cookies"] = self.cookies()

      if not request_body_within_bounds(client, content_length):
        data = AnnotatedValue(
            "",
            {
                "rem": [["!config", "x", 0, content_length]],
                "len": content_length,
            },
        )
      else:
        parsed_body = await self.parsed_body()
        if parsed_body is not None:
          data = parsed_body
        elif await self.raw_data():
          data = AnnotatedValue(
              "",
              {
                  "rem": [["!raw", "x", 0, content_length]],
                  "len": content_length,
              },
          )
        else:
          data = None

      if data is not None:
        request_info["data"] = data

    return request_info

  async def content_length(self):
    raw_data = await self.raw_data()
    if raw_data is None:
      return 0
    return len(raw_data)

  def cookies(self):
    return self.request.cookies

  async def raw_data(self):
    return await self.request.body()

  async def form(self):
    """
        curl -X POST http://localhost:8000/upload/somethign -H "Content-Type: application/x-www-form-urlencoded" -d "username=kevin&password=welcome123"
        curl -X POST http://localhost:8000/upload/somethign  -F username=Julian -F password=hello123
        """
    if multipart is None:
      return None

    return await self.request.form()

  def is_json(self):
    return _is_json_content_type(self.request.headers.get("content-type"))

  async def json(self):
    """
        curl -X POST localhost:8000/upload/something -H 'Content-Type: application/json' -d '{"login":"my_login","password":"my_password"}'
        """
    if not self.is_json():
      return None

    return await self.request.json()

  async def parsed_body(self):
    """
        curl -X POST http://localhost:8000/upload/somethign  -F username=Julian -F password=hello123 -F photo=@photo.jpg
        """
    form = await self.form()
    if form:
      data = {}
      for key, val in iteritems(form):
        if isinstance(val, UploadFile):
          size = len(await val.read())
          data[key] = AnnotatedValue("", {
              "len": size,
              "rem": [["!raw", "x", 0, size]]
          })
        else:
          data[key] = val

      return data

    json_data = await self.json()
    return json_data


def _set_transaction_name_and_source(event, transaction_style, request):
  name = ""

  if transaction_style == "endpoint":
    endpoint = request.scope.get("endpoint")
    if endpoint:
      name = transaction_from_function(endpoint) or ""

  elif transaction_style == "url":
    router = request.scope["router"]
    for route in router.routes:
      match = route.matches(request.scope)

      if match[0] == Match.FULL:
        if transaction_style == "endpoint":
          name = transaction_from_function(match[1]["endpoint"]) or ""
          break
        elif transaction_style == "url":
          name = route.path
          break

  if not name:
    event["transaction"] = _DEFAULT_TRANSACTION_NAME
    event["transaction_info"] = {"source": TRANSACTION_SOURCE_ROUTE}
    return

  event["transaction"] = name
  event["transaction_info"] = {"source": SOURCE_FOR_STYLE[transaction_style]}
