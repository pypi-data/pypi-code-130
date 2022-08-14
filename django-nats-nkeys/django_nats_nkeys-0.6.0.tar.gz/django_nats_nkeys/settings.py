import os
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model


class DjangoNatsNkeySettings:
    @property
    def NATS_NSC_DATA_DIR(self) -> str:
        """
        Defaults to $NSC_STORE
        Passed via nsc --data-dir
        """
        default = os.environ.get("NSC_STORE", "/var/lib/nats/nsc/stores")
        return getattr(settings, "NATS_NSC_DATA_DIR", default)

    @property
    def NATS_NSC_CONFIG_DIR(self) -> str:
        """
        Defaults to $NSC_HOME
        Passed via nsc --config-dir
        """
        default = os.environ.get("NSC_HOME", "/var/lib/nats/nsc/config")
        return getattr(settings, "NATS_NSC_CONFIG_DIR", default)

    @property
    def NATS_NSC_KEYSTORE_DIR(self) -> str:
        """
        Defaults to $NKEYS_PATH
        Passed via nsc --keystore-dir
        """
        default = os.environ.get("NKEYS_PATH", "/var/lib/nats/nsc/keys")
        return getattr(settings, "NATS_NSC_KEYSTORE_DIR", default)

    @property
    def NATS_NKEYS_IMPORT_DIR(self) -> str:
        return getattr(settings, "NATS_NKEYS_IMPORT_DIR", ".nats/")

    @property
    def NATS_NKEYS_EXPORT_DIR(self) -> str:
        return getattr(settings, "NATS_NKEYS_EXPORT_DIR", ".nats/")

    @property
    def NATS_SERVER_URI(self) -> str:
        return getattr(settings, "NATS_SERVER_URI", "nats://nats:4222")

    @property
    def NATS_NKEYS_OPERATOR_NAME(self) -> str:
        return getattr(settings, "NATS_NKEYS_OPERATOR_NAME", "DjangoOperator")

    def get_nats_robot_account_model_string(self) -> str:
        return getattr(
            settings,
            "NATS_ROBOT_ACCOUNT_MODEL",
            "django_nats_nkeys.NatsRobotAccount",
        )

    def get_nats_robot_account_model(self) -> Model:
        model_name = self.get_nats_robot_account_model_string()
        try:
            model = django_apps.get_model(model_name)
        except ValueError:
            raise ImproperlyConfigured(
                "NATS_ROBOT_ACCOUNT_MODEL must be of the form 'app_label.model_name'."
            )
        except LookupError:
            raise ImproperlyConfigured(
                "NATS_ROBOT_ACCOUNT_MODEL refers to model '{model}' "
                "that has not been installed.".format(model=model_name)
            )
        from django_nats_nkeys.models import AbstractNatsRobotAccount

        if not issubclass(model, AbstractNatsRobotAccount):
            raise ImproperlyConfigured(
                "NATS_ROBOT_ACCOUNT_MODEL must subclass django_nats_nkey.models.AbstractRobotAccountt"
            )
        return model

    def get_nats_robot_app_model_string(self) -> str:
        return getattr(
            settings,
            "NATS_ROBOT_APP_MODEL",
            "django_nats_nkeys.NatsRobotApp",
        )

    def get_nats_robot_app_model(self) -> Model:
        model_name = self.get_nats_robot_app_model_string()
        try:
            model = django_apps.get_model(model_name)
        except ValueError:
            raise ImproperlyConfigured(
                "NATS_ROBOT_APP_MODEL must be of the form 'app_label.model_name'."
            )
        except LookupError:
            raise ImproperlyConfigured(
                "NATS_ROBOT_APP_MODEL refers to model '{model}' "
                "that has not been installed.".format(model=model_name)
            )
        from django_nats_nkeys.models import NatsRobotApp

        if not issubclass(model, NatsRobotApp):
            raise ImproperlyConfigured(
                "NATS_ROBOT_ACCOUNT_MODEL must subclass django_nats_nkey.models.NatsRobotApp"
            )
        return model

    def get_nats_organization_owner_model_string(self) -> str:
        return getattr(
            settings,
            "NATS_ORGANIZATION_OWNER_MODEL",
            "django_nats_nkeys.NatsOrganizationOwner",
        )

    def get_NATS_ORGANIZATION_OWNER_MODEL(self) -> Model:
        model_name = self.get_nats_organization_owner_model_string()
        try:
            nats_app_model = django_apps.get_model(model_name)
        except ValueError:
            raise ImproperlyConfigured(
                "NATS_ORGANIZATION_APP_MODEL must be of the form 'app_label.model_name'."
            )
        except LookupError:
            raise ImproperlyConfigured(
                "NATS_ORGANIZATION_APP_MODEL refers to model '{model}' "
                "that has not been installed.".format(model=model_name)
            )
        from django_nats_nkeys.models import NatsOrganizationOwner

        if not issubclass(nats_app_model, NatsOrganizationOwner):
            raise ImproperlyConfigured(
                "NATS_ORGANIZATION_MODEL must subclass django_nats_nkey.models.NatsOrganizationOwner"
            )
        return nats_app_model

    def get_nats_organization_app_model_string(self) -> str:
        return getattr(
            settings,
            "NATS_ORGANIZATION_APP_MODEL",
            "django_nats_nkeys.NatsOrganizationApp",
        )

    def get_nats_organization_app_model(self) -> Model:
        model_name = self.get_nats_organization_app_model_string()
        try:
            nats_app_model = django_apps.get_model(model_name)
        except ValueError:
            raise ImproperlyConfigured(
                "NATS_ORGANIZATION_APP_MODEL must be of the form 'app_label.model_name'."
            )
        except LookupError:
            raise ImproperlyConfigured(
                "NATS_ORGANIZATION_APP_MODEL refers to model '{model}' "
                "that has not been installed.".format(model=model_name)
            )
        from django_nats_nkeys.models import AbstractNatsApp

        if not issubclass(nats_app_model, AbstractNatsApp):
            raise ImproperlyConfigured(
                "NATS_ORGANIZATION_MODEL must subclass django_nats_nkey.models.AbstractNatsApp"
            )
        return nats_app_model

    def get_nats_account_model_string(self) -> str:
        """Get the configured subscriber model as a module path string."""
        return getattr(
            settings, "NATS_ORGANIZATION_MODEL", "django_nats_nkeys.NatsOrganization"
        )

    def get_nats_account_model(self) -> Model:
        """
        Attempt to read settings.NATS_ORGANIZATION_MODEL
        This methods falls back to django_nats_nkey.models.NatsAccount if custom NATS_ORGANIZATION_MODEL is not set
        Also verifies that NATS_ORGANIZATION_MODEL is subclass of Organization model (or proxy)
        """
        model_name = self.get_nats_account_model_string()

        try:
            nats_account_model = django_apps.get_model(model_name)
        except ValueError:
            raise ImproperlyConfigured(
                "NATS_ORGANIZATION_MODEL must be of the form 'app_label.model_name'."
            )
        except LookupError:
            raise ImproperlyConfigured(
                "NATS_ORGANIZATION_MODEL refers to model '{model}' "
                "that has not been installed.".format(model=model_name)
            )
        from django_nats_nkeys.models import NatsOrganization

        if not issubclass(nats_account_model, NatsOrganization):
            raise ImproperlyConfigured(
                "NATS_ORGANIZATION_MODEL must subclass django_nats_nkeys.models.NatsAccount"
            )
        return nats_account_model

    def get_nats_user_model_string(self) -> str:
        """Get the configured subscriber model as a module path string."""
        return getattr(
            settings,
            "NATS_ORGANIZATION_USER_MODEL",
            "django_nats_nkeys.NatsOrganizationUser",
        )

    def get_nats_user_model(self) -> Model:
        """
        Attempt to read settings.NATS_ORGANIZATION_USER_MODEL
        This methods falls back to django_nats_nkey.models.NatsUser if custom NATS_ORGANIZATION_MODEL is not set
        Also verifies that NATS_ORGANIZATION_MODEL is subclass of Organization model (or proxy)
        """
        model_name = self.get_nats_user_model_string()

        try:
            nats_user_model = django_apps.get_model(model_name)
        except ValueError:
            raise ImproperlyConfigured(
                "NATS_ORGANIZATION_USER_MODEL must be of the form 'app_label.model_name'."
            )
        except LookupError:
            raise ImproperlyConfigured(
                "NATS_ORGANIZATION_USER_MODEL refers to model '{model}' "
                "that has not been installed.".format(model=model_name)
            )
        from django_nats_nkeys.models import NatsOrganizationUser

        if not issubclass(nats_user_model, NatsOrganizationUser):
            raise ImproperlyConfigured(
                "NATS_ORGANIZATION_USER_MODEL must subclass or proxy django_nats_nkeys.models.NatsOrganizationUser"
            )
        return nats_user_model


nats_nkeys_settings = DjangoNatsNkeySettings()
