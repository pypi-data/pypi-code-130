from __future__ import absolute_import

import sys

from warden_sdk.hub import Hub
from warden_sdk.integrations import Integration
from warden_sdk.scope import add_global_event_processor


class ArgvIntegration(Integration):
  identifier = "argv"

  @staticmethod
  def setup_once():
    # type: () -> None
    @add_global_event_processor
    def processor(event, hint):
      if Hub.current.get_integration(ArgvIntegration) is not None:
        extra = event.setdefault("extra", {})
        # If some event processor decided to set extra to e.g. an
        # `int`, don't crash. Not here.
        if isinstance(extra, dict):
          extra["sys.argv"] = sys.argv

      return event
