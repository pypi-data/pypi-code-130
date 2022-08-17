"""Service."""

from pydantic import BaseSettings as UserSettings  # noqa
from spec.fn import load_env
from spec import load_spec

from service.log import JSONFormatter, ServiceFormatter  # noqa
from service.app import App, create


load_env()
spec = load_spec()
