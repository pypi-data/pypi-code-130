# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from redturtle.chefcookie.defaults import ANCHOR_MAPPING
from redturtle.chefcookie.defaults import IFRAMES_MAPPING
from redturtle.chefcookie.interfaces import IChefCookieSettings
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "redturtle.chefcookie:uninstall",
        ]


def post_install(context):
    """Post install script"""
    # set defaults to some registry keys
    api.portal.set_registry_record(
        "links_mapping", ANCHOR_MAPPING, interface=IChefCookieSettings
    )
    api.portal.set_registry_record(
        "iframes_mapping", IFRAMES_MAPPING, interface=IChefCookieSettings
    )


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
