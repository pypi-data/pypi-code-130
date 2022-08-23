from django.conf import settings
from django.utils.module_loading import import_string

USER_SETTINGS = getattr(settings, "REST_EMAIL_MANAGER", None)

DEFAULTS = {
    "EMAIL_ADDRESS_SERIALIZER": (
        "rest_email_manager.serializers.EmailAddressSerializer"
    ),
    "EMAIL_ADDRESS_KEY_SERIALIZER": (
        "rest_email_manager.serializers.EmailAddressKeySerializer"
    ),
    "EMAIL_VERIFICATION_URL": "account/email/verify/{key}",
    "SEND_VERIFICATION_EMAIL": (
        "rest_email_manager.utils.send_verification_email"
    ),
    "SEND_NOTIFICATION_EMAIL": (
        "rest_email_manager.utils.send_notification_email"
    ),
}

IMPORT_STRINGS = [
    "EMAIL_ADDRESS_SERIALIZER",
    "EMAIL_ADDRESS_KEY_SERIALIZER",
    "SEND_VERIFICATION_EMAIL",
    "SEND_NOTIFICATION_EMAIL",
]


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import %r for setting %r. %s: %s." % (
            val,
            setting_name,
            e.__class__.__name__,
            e,
        )
        raise ImportError(msg)


class RestEmailManagerSettings:
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        self._user_settings = user_settings or {}
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "REST_EMAIL_MANAGER", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid RestEmailManager setting: %s" % attr)
        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if val and attr in self.import_strings:
            val = perform_import(val, attr)

        return val


rest_email_manager_settings = RestEmailManagerSettings(
    USER_SETTINGS, DEFAULTS, IMPORT_STRINGS
)
