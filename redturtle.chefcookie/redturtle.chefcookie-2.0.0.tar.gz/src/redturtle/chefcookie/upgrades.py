# -*- coding: utf-8 -*-
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from redturtle.chefcookie.interfaces import IChefCookieSettings
from redturtle.chefcookie.defaults import LABELS
from zope.component import getUtility
from zope.interface import alsoProvides

import json
import logging
import six

logger = logging.getLogger(__name__)

DEFAULT_PROFILE = "profile-redturtle.chefcookie:default"


def update_profile(context, profile, run_dependencies=True):
    context.runImportStepFromProfile(DEFAULT_PROFILE, profile, run_dependencies)


def update_registry(context):
    update_profile(context, "plone.app.registry", run_dependencies=False)
    logger.info("Update registry")


def update_to_1002(context):
    alsoProvides(context.REQUEST, IDisableCSRFProtection)
    update_registry(context)

    api.portal.set_registry_record("enable_cc", True, interface=IChefCookieSettings)


def to_1100(context):
    registry = getUtility(IRegistry)

    # merge labels
    analytics = registry[
        "redturtle.chefcookie.interfaces.IChefCookieSettings.analytics_cookies_labels"
    ]
    functional = registry[
        "redturtle.chefcookie.interfaces.IChefCookieSettings.functional_cookies_labels"
    ]

    analytics_id = registry[
        "redturtle.chefcookie.interfaces.IChefCookieSettings.analytics_id"
    ]

    new_conf = {
        "techcookies": json.loads(functional),
    }
    if analytics_id:
        new_conf["analytics"] = json.loads(analytics)

    if six.PY2:
        new_conf_json = json.dumps(new_conf, indent=4).decode("utf-8")
    else:
        new_conf_json = json.dumps(new_conf, indent=4)

    update_registry(context)

    api.portal.set_registry_record(
        "technical_cookies_specific_labels",
        new_conf_json,
        interface=IChefCookieSettings,
    )

    api.portal.set_registry_record("enable_cc", True, interface=IChefCookieSettings)

    # add close label
    general = json.loads(
        registry["redturtle.chefcookie.interfaces.IChefCookieSettings.general_labels"]
    )
    if "close" not in general:
        general["close"] = LABELS["general"]["close"]
        if six.PY2:
            new_general = json.dumps(general, indent=4).decode("utf-8")
        else:
            new_general = json.dumps(general, indent=4)

        api.portal.set_registry_record(
            "general_labels",
            new_general,
            interface=IChefCookieSettings,
        )

    # convert policy_url to new format
    lang = api.portal.get_default_language()
    old_policy_url = registry[
        "redturtle.chefcookie.interfaces.IChefCookieSettings.policy_url"
    ]
    new_policy_url = {lang: old_policy_url}
    if six.PY2:
        new_policy_url = json.dumps(new_policy_url, indent=4).decode("utf-8")
    else:
        new_policy_url = json.dumps(new_policy_url, indent=4)

    api.portal.set_registry_record(
        "policy_url",
        new_policy_url,
        interface=IChefCookieSettings,
    )
