"""Global centralized class to manage all instances.

Hub centralizes and manages all Clients that are instantiated. This allows us to globally access Clients and puts the Hub in a ContextVars for easier management across different threads if used in async.

This module also initializes the warden_sdk through th `init()` module.

  Typical usage example:

  import warden_sdk as warden
  warden_sdk.init(...)

Code reference:
- [warden_sdk](https://github.com/getwarden/warden-python/blob/master/warden_sdk/hub.py)
"""
import copy
import sys

from datetime import datetime
from contextlib import contextmanager

from warden_sdk.scope import Scope
from warden_sdk.client import Client
from warden_sdk.tracing import Span, Transaction
from warden_sdk.session import Session
from warden_sdk.utils import (
    ContextVar,
    logger,
    exc_info_from_error,
    event_from_exception,
)

from typing import (
    Union,
    Any,
    Optional,
    Tuple,
    Dict,
    List,
    Callable,
    Generator,
    Type,
    TypeVar,
    overload,
    ContextManager,
)

T = TypeVar("T")

# Create local and global context to handle the global Hub.
_local = ContextVar("warden_current_hub")


def _update_scope(base, scope_change, scope_kwargs):
  # type: (Scope, Optional[Any], Dict[str, Any]) -> Scope
  if scope_change and scope_kwargs:
    raise TypeError("cannot provide scope and kwargs")
  if scope_change is not None:
    final_scope = copy.copy(base)
    if callable(scope_change):
      scope_change(final_scope)
    else:
      final_scope.update_from_scope(scope_change)
  elif scope_kwargs:
    final_scope = copy.copy(base)
    final_scope.update_from_kwargs(**scope_kwargs)
  else:
    final_scope = base
  return final_scope


def _should_send_default_pii() -> bool:
  client = Hub.current.client
  if not client:
    return False
  return client.options["send_default_pii"]


class _InitGuard(object):
  """Protects the initialization by closing the previous client.
   """

  def __init__(self, client) -> None:
    self._client = client

  def __enter__(self):
    # type: () -> _InitGuard
    return self

  def __exit__(self, exc_type, exc_value, tb):
    c = self._client
    if c is not None:
      c.close()


def _init(*args, **kwargs):
  """Initialize `warden_sdk`.

  Setups up the initial Client on the global Hub class.

  Args:
      *args
      **kwargs

  Returns:
      Instantiated class of InitGuard that will close the client when warden is initialized again.
  """
  client = Client(*args, **kwargs)
  Hub.current.bind_client(client)
  rv = _InitGuard(client)
  return rv


init = (lambda: _init)()


def with_metaclass(meta, *bases) -> Any:
  # type: (Any, *Any) -> Any
  class MetaClass(type):

    def __new__(metacls, name, this_bases, d) -> Any:
      # type: (Any, Any, Any, Any) -> Any
      return meta(name, bases, d)

  return type.__new__(MetaClass, "temporary_class", (), {})


class HubMeta(type):
  """Base class for Hub to get current/global Hub.
   """

  @property
  def current(cls):
    """Returns the current instance of the hub."""
    rv = _local.get(None)
    if rv is None:
      rv = Hub(GLOBAL_HUB)
      _local.set(rv)
    return rv

  @property
  def main(cls):
    """Returns the main instance of the hub."""
    return GLOBAL_HUB


class _ScopeManager(object):

  def __init__(self, hub):
    # type: (Hub) -> None
    self._hub = hub
    self._original_len = len(hub._stack)
    self._layer = hub._stack[-1]

  def __enter__(self):
    # type: () -> Scope
    scope = self._layer[1]
    assert scope is not None
    return scope

  def __exit__(self, exc_type, exc_value, tb):
    # type: (Any, Any, Any) -> None
    current_len = len(self._hub._stack)
    if current_len < self._original_len:
      logger.error(
          "Scope popped too soon. Popped %s scopes too many.",
          self._original_len - current_len,
      )
      return
    elif current_len > self._original_len:
      logger.warning(
          "Leaked %s scopes: %s",
          current_len - self._original_len,
          self._hub._stack[self._original_len:],
      )

    layer = self._hub._stack[self._original_len - 1]
    del self._hub._stack[self._original_len - 1:]

    if layer[1] != self._layer[1]:
      logger.error(
          "Wrong scope found. Meant to pop %s, but popped %s.",
          layer[1],
          self._layer[1],
      )
    elif layer[0] != self._layer[0]:
      warning = (
          "init() called inside of pushed scope. This might be entirely "
          "legitimate but usually occurs when initializing the SDK inside "
          "a request handler or task/job function. Try to initialize the "
          "SDK as early as possible instead.")
      logger.warning(warning)


class Hub(with_metaclass(HubMeta)):
  """The hub wraps the concurrency management of the SDK.  Each thread has
  its own hub but the hub might transfer with the flow of execution if
  context vars are available.
  
  If the hub is used with a with statement it's temporarily activated.
  """
  _stack: List[Tuple[Optional[Client], Scope]] = None    # type: ignore

  def __init__(
      self,
      client_or_hub=None,    # type: Optional[Union[Hub, Client]]
      scope: Optional[Scope] = None,    # type: ignore
  ):
    if isinstance(client_or_hub, Hub):
      hub = client_or_hub
      client, other_scope = hub._stack[-1]
      if scope is None:
        scope = copy.copy(other_scope)
    else:
      client = client_or_hub
    if scope is None:
      scope: Scope = Scope()

    self._stack = [(client, scope)]
    self._last_event_id: Optional[str] = None    # type: Optional[str]
    self._old_hubs: List[__class__] = []    # type: List[Hub]

  def __enter__(self):
    self._old_hubs.append(Hub.current)
    _local.set(self)
    return self

  def __exit__(
      self,
      exc_type,    # type: Optional[type]
      exc_value,    # type: Optional[BaseException]
      tb,    # type: Optional[Any]
  ):
    old = self._old_hubs.pop()
    _local.set(old)

  def run(self, callback):
    """Runs a callback in the context of the hub.  Alternatively the
      with statement can be used on the hub directly.
      """
    with self:
      return callback()

  @property
  def client(self) -> Optional[Client]:
    """Returns the current client on the hub."""
    return self._stack[-1][0]    # type: ignore

  @property
  def scope(self) -> Scope:
    """Returns the current scope on the hub."""
    return self._stack[-1][1]    # type: ignore

  def last_event_id(self) -> Optional[str]:
    """Returns the last event ID."""
    return self._last_event_id

  def bind_client(
      self,
      new: Optional[Client],
  ):
    """Binds a new client to the hub."""
    top = self._stack[-1]
    self._stack[-1] = (new, top[1])

  def capture_event(
      self,
      event,    # type: Event
      hint=None,    # type: Optional[Hint]
      scope: Optional[Any] = None,
      **scope_args: Any,
  ) -> Optional[str]:
    """Captures an event. Alias of :py:meth:`warden_sdk.Client.capture_event`."""
    client, top_scope = self._stack[-1]
    scope = _update_scope(top_scope, scope, scope_args)
    if client is not None:
      is_transaction = event.get("type") == "transaction"
      rv = client.capture_event(event, hint, scope)
      if rv is not None and not is_transaction:
        self._last_event_id = rv
      return rv
    return None

  def capture_message(
      self,
      message: str,
      level: Optional[str] = None,
      scope: Optional[Any] = None,
      **scope_args: Any,
  ) -> Optional[str]:
    """Captures a message.  The message is just a string.  If no level
      is provided the default level is `info`.

      Returns:
         An `event_id` if the SDK decided to send the event (see :py:meth:`warden_sdk.Client.capture_event`).
      """
    if self.client is None:
      return None
    if level is None:
      level = "info"
    return self.capture_event(
        {
            "message": message,
            "level": level
        },
        scope=scope,
        **scope_args,
    )

  def capture_exception(
      self,
      error=None,    # type: Optional[Union[BaseException, ExcInfo]]
      scope: Optional[Any] = None,
      **scope_args: Any,
  ) -> Optional[str]:
    """Captures an exception.

      Args:
         error: An exception to catch. If `None`, `sys.exc_info()` will be used.

      Returns
         An `event_id` if the SDK decided to send the event (see :py:meth:`warden_sdk.Client.capture_event`).
      """
    client = self.client
    if client is None:
      return None
    if error is not None:
      exc_info = exc_info_from_error(error)
    else:
      exc_info = sys.exc_info()

    event, hint = event_from_exception(exc_info, client_options=client.options)
    try:
      return self.capture_event(
          event,
          hint=hint,
          scope=scope,
          **scope_args,
      )
    except Exception:
      self._capture_internal_exception(sys.exc_info())

    return None

  def _capture_internal_exception(
      self,
      exc_info: Any,
  ) -> Any:
    """ Capture an exception that is likely caused by a bug in the SDK itself.
      
      These exceptions do not end up in Warden and are just logged instead.
      """
    logger.error("Internal error in warden_sdk", exc_info=exc_info)

  def add_breadcrumb(
      self,
      crumb=None,    # type: Optional[Breadcrumb]
      hint=None,    # type: Optional[BreadcrumbHint]
      **kwargs    # type: Any
  ) -> None:
    """
        Adds a breadcrumb.
        :param crumb: Dictionary with the data as the warden v7/v8 protocol expects.
        :param hint: An optional value that can be used by `before_breadcrumb`
            to customize the breadcrumbs that are emitted.
        """
    client, scope = self._stack[-1]
    if client is None:
      logger.info("Dropped breadcrumb because no client bound")
      return

    crumb = dict(crumb or ())    # type: Breadcrumb
    crumb.update(kwargs)
    if not crumb:
      return

    hint = dict(hint or ())    # type: Hint

    if crumb.get("timestamp") is None:
      crumb["timestamp"] = datetime.utcnow()
    if crumb.get("type") is None:
      crumb["type"] = "default"

    if client.options["before_breadcrumb"] is not None:
      new_crumb = client.options["before_breadcrumb"](crumb, hint)
    else:
      new_crumb = crumb

    if new_crumb is not None:
      scope._breadcrumbs.append(new_crumb)
    else:
      logger.info("before breadcrumb dropped breadcrumb (%s)", crumb)

    max_breadcrumbs = client.options["max_breadcrumbs"]    # type: int
    while len(scope._breadcrumbs) > max_breadcrumbs:
      scope._breadcrumbs.popleft()

  def start_span(
      self,
      span=None,    # type: Optional[Span]
      **kwargs    # type: Any
  ):
    # type: (...) -> Span
    """
        Create and start timing a new span whose parent is the currently active
        span or transaction, if any. The return value is a span instance,
        typically used as a context manager to start and stop timing in a `with`
        block.
        Only spans contained in a transaction are sent to Warden. Most
        integrations start a transaction at the appropriate time, for example
        for every incoming HTTP request. Use `start_transaction` to start a new
        transaction when one is not already in progress.
        """
    # TODO: consider removing this in a future release.
    # This is for backwards compatibility with releases before
    # start_transaction existed, to allow for a smoother transition.
    if isinstance(span, Transaction) or "transaction" in kwargs:
      deprecation_msg = (
          "Deprecated: use start_transaction to start transactions and "
          "Transaction.start_child to start spans.")
      if isinstance(span, Transaction):
        logger.warning(deprecation_msg)
        return self.start_transaction(span)
      if "transaction" in kwargs:
        logger.warning(deprecation_msg)
        name = kwargs.pop("transaction")
        return self.start_transaction(name=name, **kwargs)

    if span is not None:
      return span

    kwargs.setdefault("hub", self)

    span = self.scope.span
    if span is not None:
      return span.start_child(**kwargs)

    return Span(**kwargs)

  def start_transaction(
      self,
      transaction=None,    # type: Optional[Transaction]
      **kwargs    # type: Any
  ):
    # type: (...) -> Transaction
    """
      Start and return a transaction.
      Start an existing transaction if given, otherwise create and start a new
      transaction with kwargs.
      This is the entry point to manual tracing instrumentation.
      A tree structure can be built by adding child spans to the transaction,
      and child spans to other spans. To start a new child span within the
      transaction or any span, call the respective `.start_child()` method.
      Every child span must be finished before the transaction is finished,
      otherwise the unfinished spans are discarded.
      When used as context managers, spans and transactions are automatically
      finished at the end of the `with` block. If not using context managers,
      call the `.finish()` method.
      When the transaction is finished, it will be sent to Warden with all its
      finished child spans.
      """
    custom_sampling_context = kwargs.pop("custom_sampling_context", {})

    # if we haven't been given a transaction, make one
    if transaction is None:
      kwargs.setdefault("hub", self)
      transaction = Transaction(**kwargs)

    # use traces_sample_rate, traces_sampler, and/or inheritance to make a
    # sampling decision
    sampling_context = {
        "transaction_context": transaction.to_json(),
        "parent_sampled": transaction.parent_sampled,
    }
    sampling_context.update(custom_sampling_context)
    transaction._set_initial_sampling_decision(
        sampling_context=sampling_context)

    # we don't bother to keep spans if we already know we're not going to
    # send the transaction
    if transaction.sampled:
      max_spans = (self.client and
                   self.client.options["_experiments"].get("max_spans")) or 1000
      transaction.init_span_recorder(maxlen=max_spans)

    return transaction

  @overload
  def push_scope(    # noqa: F811
      self,
      callback=None    # type: Optional[None]
  ):
    # type: (...) -> ContextManager[Scope]
    pass

  @overload
  def push_scope(    # noqa: F811
      self,
      callback    # type: Callable[[Scope], None]
  ):
    # type: (...) -> None
    pass

  def push_scope(    # noqa
      self,
      callback=None    # type: Optional[Callable[[Scope], None]]
  ):
    # type: (...) -> Optional[ContextManager[Scope]]
    """
      Pushes a new layer on the scope stack.
      :param callback: If provided, this method pushes a scope, calls
         `callback`, and pops the scope again.
      :returns: If no `callback` is provided, a context manager that should
         be used to pop the scope again.
      """
    if callback is not None:
      with self.push_scope() as scope:
        callback(scope)
      return None

    client, scope = self._stack[-1]
    new_layer = (client, copy.copy(scope))
    self._stack.append(new_layer)

    return _ScopeManager(self)

  def pop_scope_unsafe(self):
    # type: () -> Tuple[Optional[Client], Scope]
    """
      Pops a scope layer from the stack.
      Try to use the context manager :py:meth:`push_scope` instead.
      """
    rv = self._stack.pop()
    assert self._stack, "stack must have at least one layer"
    return rv

  @overload
  def configure_scope(    # noqa: F811
      self,
      callback=None    # type: Optional[None]
  ):
    # type: (...) -> ContextManager[Scope]
    pass

  @overload
  def configure_scope(    # noqa: F811
      self,
      callback    # type: Callable[[Scope], None]
  ):
    # type: (...) -> None
    pass

  def configure_scope(    # noqa
      self,
      callback=None    # type: Optional[Callable[[Scope], None]]
  ):    # noqa
    # type: (...) -> Optional[ContextManager[Scope]]
    """
      Reconfigures the scope.
      :param callback: If provided, call the callback with the current scope.
      :returns: If no callback is provided, returns a context manager that returns the scope.
      """

    client, scope = self._stack[-1]
    if callback is not None:
      if client is not None:
        callback(scope)

      return None

    @contextmanager
    def inner():
      # type: () -> Generator[Scope, None, None]
      if client is not None:
        yield scope
      else:
        yield Scope()

    return inner()

  def start_session(
      self,
      session_mode="application"    # type: str
  ):
    # type: (...) -> None
    """Starts a new session."""
    self.end_session()
    client, scope = self._stack[-1]
    scope._session = Session(
        release=client.options["release"] if client else None,
        environment=client.options["environment"] if client else None,
        user=scope._user,
        session_mode=session_mode,
    )

  def end_session(self):
    # type: (...) -> None
    """Ends the current session if there is one."""
    client, scope = self._stack[-1]
    session = scope._session
    self.scope._session = None

    if session is not None:
      session.close()
      if client is not None:
        client.capture_session(session)

  def stop_auto_session_tracking(self):
    # type: (...) -> None
    """Stops automatic session tracking.
      This temporarily session tracking for the current scope when called.
      To resume session tracking call `resume_auto_session_tracking`.
      """
    self.end_session()
    client, scope = self._stack[-1]
    scope._force_auto_session_tracking = False

  def resume_auto_session_tracking(self):
    # type: (...) -> None
    """Resumes automatic session tracking for the current scope if
      disabled earlier.  This requires that generally automatic session
      tracking is enabled.
      """
    client, scope = self._stack[-1]
    scope._force_auto_session_tracking = None

  def flush(self):
    client = self.client
    client.close()
    pass

  def get_integration(
      self,
      name_or_class    # type: Union[str, Type[Integration]]
  ):
    # type: (...) -> Any
    """Returns the integration for this hub by name or class.  If there
        is no client bound or the client does not have that integration
        then `None` is returned.
        If the return value is not `None` the hub is guaranteed to have a
        client attached.
        """
    if isinstance(name_or_class, str):
      integration_name = name_or_class
    elif name_or_class.identifier is not None:
      integration_name = name_or_class.identifier
    else:
      raise ValueError("Integration has no name")

    client = self.client
    if client is not None:
      rv = client.integrations.get(integration_name)
      if rv is not None:
        return rv

  def iter_trace_propagation_headers(self, span=None):
    # type: (Optional[Span]) -> Generator[Tuple[str, str], None, None]
    """
        Return HTTP headers which allow propagation of trace data. Data taken
        from the span representing the request, if available, or the current
        span on the scope if not.
        """
    span = span or self.scope.span
    if not span:
      return

    client = self._stack[-1][0]

    propagate_traces = client and client.options["propagate_traces"]
    if not propagate_traces:
      return

    yield "warden-trace", span.to_traceparent()

  def set_test_user(self,
                    user_fid: Optional[str] = None,
                    user_scope: Optional[Union[str, List[str]]] = None):
    client = self.client
    if client is None:
      return None
    return client.set_test_user(user_fid, user_scope)

  def debug(self, val: Optional[bool] = None) -> bool:
    client = self.client
    if client is None:
      return None
    return client.debug(val)

  def env(self, env: Optional[str] = None) -> str:
    client = self.client
    if client is None:
      return None
    return client.env(env)


# Instantiate a Global Hub class and set it into the local ContextVars
GLOBAL_HUB = Hub()
_local.set(GLOBAL_HUB)
