from __future__ import absolute_import

import sys
from threading import Thread, current_thread

from warden_sdk import Hub
from warden_sdk._compat import reraise
from warden_sdk.integrations import Integration
from warden_sdk.utils import event_from_exception, capture_internal_exceptions


class ThreadingIntegration(Integration):
  identifier = "threading"

  def __init__(self, propagate_hub=False):
    self.propagate_hub = propagate_hub

  @staticmethod
  def setup_once():
    old_start = Thread.start

    def warden_start(self, *a, **kw):
      hub = Hub.current
      integration = hub.get_integration(ThreadingIntegration)
      if integration is not None:
        if not integration.propagate_hub:
          hub_ = None
        else:
          hub_ = Hub(hub)
        # Patching instance methods in `start()` creates a reference cycle if
        # done in a naive way. See
        # https://github.com/getwarden/warden-python/pull/434
        #
        # In threading module, using current_thread API will access current thread instance
        # without holding it to avoid a reference cycle in an easier way.
        with capture_internal_exceptions():
          new_run = _wrap_run(hub_, getattr(self.run, "__func__", self.run))
          self.run = new_run    # type: ignore

      return old_start(self, *a, **kw)

    Thread.start = warden_start    # type: ignore


def _wrap_run(parent_hub, old_run_func):

  def run(*a, **kw):
    hub = parent_hub or Hub.current
    with hub:
      try:
        self = current_thread()
        return old_run_func(self, *a, **kw)
      except Exception:
        reraise(*_capture_exception())

  return run    # type: ignore


def _capture_exception():
  hub = Hub.current
  exc_info = sys.exc_info()

  if hub.get_integration(ThreadingIntegration) is not None:
    # If an integration is there, a client has to be there.
    client = hub.client

    event, hint = event_from_exception(
        exc_info,
        client_options=client.options,
        mechanism={
            "type": "threading",
            "handled": False
        },
    )
    hub.capture_event(event, hint=hint)

  return exc_info
