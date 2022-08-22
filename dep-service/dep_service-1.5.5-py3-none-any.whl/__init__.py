"""Service."""

from pydantic import BaseSettings as UserSettings  # noqa

from spec import load_spec

from spec.fn import load_env

from spec.service.configure import App, create  # noqa
from service.log import JSONFormatter, ServiceFormatter  # noqa


load_env()
spec = load_spec()
