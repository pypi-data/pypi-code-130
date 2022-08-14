import subprocess
from django.db import models
from organizations.abstract import (
    AbstractOrganization,
    AbstractOrganizationUser,
    AbstractOrganizationOwner,
    AbstractOrganizationInvitation,
)
from organizations.managers import OrgManager, ActiveOrgManager

from coolname import generate_slug


# ref: https://django-organizations.readthedocs.io/en/latest/cookbook.html#multiple-organizations-with-simple-inheritance


class NatsMessageExportType(models.TextChoices):
    SERVICE = (
        "service",
        "Export is a service: https://docs.nats.io/using-nats/nats-tools/nsc/services",
    )
    STREAM = (
        "stream",
        "Export is a stream: https://docs.nats.io/using-nats/nats-tools/nsc/streams",
    )


class NatsMessageExport(models.Model):

    name = models.CharField(unique=True, max_length=255)
    subject_pattern = models.CharField(unique=True, max_length=255)
    public = models.BooleanField()
    export_type = models.CharField(max_length=8, choices=NatsMessageExportType.choices)


class NatsOrganizationManager(OrgManager):
    def create_nsc(self, **kwargs):
        from django_nats_nkeys.services import nsc_add_account

        # create django model
        org = self.create(**kwargs)
        # try create nsc account
        return nsc_add_account(org)


class ActiveNatsOrganizationManager(NatsOrganizationManager, ActiveOrgManager):
    pass


def _default_name():
    return generate_slug(3)


class NatsOrganization(AbstractOrganization):

    objects = NatsOrganizationManager()
    active = ActiveNatsOrganizationManager()

    json = models.JSONField(
        max_length=255, help_text="Output of `nsc describe account`", default=dict
    )
    imports = models.ManyToManyField(
        NatsMessageExport, related_name="nats_organization_imports"
    )
    exports = models.ManyToManyField(
        NatsMessageExport, related_name="nats_organization_exports"
    )


class NatsOrganizationUserManager(models.Manager):
    def create_nsc(self, **kwargs):
        from django_nats_nkeys.services import (
            run_nsc_and_log_output,
            save_describe_json,
        )

        org_user = self.create(**kwargs)
        try:
            # add organization user for account
            run_nsc_and_log_output(
                [
                    "nsc",
                    "add",
                    "user",
                    "--account",
                    org_user.organization.name,
                    "--name",
                    org_user.app_name,
                    "-K",
                    "service",
                ]
            )
        except subprocess.CalledProcessError as e:
            # nsc add account command returned "Error: the account "<name>" already exists"
            # we can proceed to saving output of `nsc describe account <name> --json``
            if "already exists" in e.stderr:
                pass
            # re-raise other errors
            raise e
        save_describe_json(org_user.name, org_user)
        return org_user


class NatsOrganizationUser(AbstractOrganizationUser):
    """
    Corresponds to a NATS user/client, intended for use for a human who owns one or more NatsApp instances and wants to publish/subscribe to all apps via signed credential.
    """

    objects = NatsOrganizationUserManager()
    app_name = models.CharField(max_length=255, default=_default_name)
    json = models.JSONField(
        max_length=255, help_text="Output of `nsc describe account`", default=dict
    )


class AbstractNatsApp(models.Model):
    """
    Corresponds to a NATS user/client within an Account group, intended for use by application
    https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts
    """

    class Meta:
        abstract = True

    app_name = models.CharField(max_length=255, default=_default_name)
    json = models.JSONField(
        max_length=255, help_text="Output of `nsc describe account`", default=dict
    )

    allow_pub = models.CharField(
        max_length=255,
        null=True,
        help_text="add publish permissions, comma separated list. equivalent to `nsc add user ... --allow-pub=<permissions>`",
    )

    allow_pubsub = models.CharField(
        max_length=255,
        null=True,
        help_text="add publish/subscribe permissions, comma separated list. equivalent to `nsc add user ... --allow-pubsub=<permissions>`",
    )

    allow_sub = models.CharField(
        max_length=255,
        null=True,
        help_text="add subscribe permissions, comma separated list. equivalent to `nsc add user ... --allow-sub=<permissions>`",
    )
    deny_pub = models.CharField(
        max_length=255,
        null=True,
        help_text="deny publish permissions, comma separated list. equivalent to `nsc add user ... --deny-pub=<permissions>`",
    )

    deny_pubsub = models.CharField(
        max_length=255,
        null=True,
        help_text="deny publish/subscribe permissions, comma separated list. equivalent to `nsc add user ... --deny-pubsub=<permissions>`",
    )

    deny_sub = models.CharField(
        max_length=255,
        null=True,
        help_text="deny subscribe permissions, comma separated list. equivalent to `nsc add user ... --deny-sub=<permissions>`",
    )


class NatsOrganizationAppManager(models.Manager):
    def create_nsc(self, **kwargs):
        from django_nats_nkeys.services import nsc_add_app

        obj = self.create(**kwargs)
        return nsc_add_app(obj.organization.name, obj.app_name, obj)


class NatsOrganizationApp(AbstractNatsApp):
    """
    Corresponds to a NATS user/client within an Account group
    https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts
    """

    objects = NatsOrganizationAppManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["app_name", "organization_user"],
                name="unique_app_name_per_org_user",
            )
        ]

    organization_user = models.ForeignKey(
        NatsOrganizationUser, on_delete=models.CASCADE, related_name="nats_apps"
    )
    organization = models.ForeignKey(
        NatsOrganization,
        on_delete=models.CASCADE,
        related_name="nats_apps",
    )


class NatsOrganizationOwner(AbstractOrganizationOwner):
    """Identifies ONE user, by AccountUser, to be the owner"""

    pass


class NatsAccountInvitation(AbstractOrganizationInvitation):
    """Stores invitations for adding users to organizations"""

    pass


class NatsRobotAccountManager(models.Manager):
    def create_nsc(self, **kwargs):
        from django_nats_nkeys.services import nsc_add_account

        # create django model
        obj = self.create(**kwargs)
        # try create nsc account
        # import pdb

        # pdb.set_trace()
        return nsc_add_account(obj)


class AbstractNatsRobotAccount(models.Model):

    objects = NatsRobotAccountManager()

    class Meta:
        abstract = True

    name = models.CharField(unique=True, max_length=255)
    json = models.JSONField(
        max_length=255, help_text="Output of `nsc describe account`", default=dict
    )
    imports = models.ManyToManyField(
        NatsMessageExport, related_name="nats_robot_imports"
    )
    exports = models.ManyToManyField(
        NatsMessageExport, related_name="nats_robot_exports"
    )


class NatsRobotAccount(AbstractNatsRobotAccount):
    pass


class NatsRobotAppManager(models.Manager):
    def create_nsc(self, **kwargs):
        from django_nats_nkeys.services import nsc_add_app

        obj = self.create(**kwargs)
        return nsc_add_app(obj.account.name, obj.app_name, obj)


class NatsRobotApp(AbstractNatsApp):
    objects = NatsRobotAppManager()
    account = models.ForeignKey(
        NatsRobotAccount,
        related_name="robot_apps",
        on_delete=models.CASCADE,
    )
