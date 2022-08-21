from django.apps import AppConfig


class OwntracksConfig(AppConfig):
    name = "owntracks"

    def ready(self):
        from . import signals  # NOQA
