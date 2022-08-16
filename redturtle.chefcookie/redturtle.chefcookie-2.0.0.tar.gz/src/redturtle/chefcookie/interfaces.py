# -*- coding: utf-8 -*-
from redturtle.chefcookie import _
from redturtle.chefcookie.defaults import GENERAL_LABELS
from redturtle.chefcookie.defaults import HEADER_LABELS
from redturtle.chefcookie.defaults import PROFILING_COOKIES_LABELS
from redturtle.chefcookie.defaults import PROFILING_COOKIES_SPECIFIC_LABELS
from redturtle.chefcookie.defaults import TECHNICAL_COOKIES_LABELS
from redturtle.chefcookie.defaults import TECHNICAL_COOKIES_SPECIFIC_LABELS
from zope import schema
from zope.interface import Invalid
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

try:
    from plone.supermodel.model import Schema
except ImportError:
    from zope.interface import Interface

    Schema = Interface

import json


def validate_cfg_json(value):
    """check that we have at least valid json and its a dict"""
    try:
        jv = json.loads(value)
    except ValueError as e:
        message = getattr(e, "message", str(e))
        raise Invalid(
            _(
                "invalid_json",
                "JSON is not valid, parser complained: ${message}",
                mapping={
                    "message": "{msg} {pos}".format(
                        msg=message, pos=getattr(e, "pos", "")
                    ),
                },
            )
        )
    if not isinstance(jv, dict):
        raise Invalid(_("invalid_cfg_no_dict", "JSON root must be a mapping (dict)"))
    return True


class IRedturtleChefcookieLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IChefCookieSettingsConfigs(Schema):
    enable_cc = schema.Bool(
        title=_(
            "chefcookie_enable_label",
            default=u"Enable chefcookie",
        ),
        description=_(
            "chefcookie_only_enable_chefcookie_help",
            default=u"Select to use chefcookie",
        ),
        required=False,
    )
    show_settings_icon = schema.Bool(
        title=_(
            "show_settings_icon_label",
            default=u"Show settings icon",
        ),
        description=_(
            "show_settings_icon_help",
            default=u"If selected, an icon that opens cookie settings will be "
            "displayed on the right side of the page. You should always allow "
            "users to change their settings, so if you disable this option, be "
            "sure to insert a link somewhere in the page (e.g. in the footer). "
            'It should be an "a" tag with data-cc-open-settings attribute.',
        ),
        required=False,
        default=True,
    )
    cookie_name = schema.TextLine(
        title=_("chefcookie_cookie_prefix_label", default=u"Cookie prefix"),
        description=_(
            "chefcookie_cookie_prefix_help",
            default=u"Set the cookie prefix",
        ),
        default=u"cc_",
        required=True,
    )
    registry_endpoint = schema.TextLine(
        title=_("chefcookie_registry_endpoint_label", default=u"Registry endpoint"),
        description=_(
            "chefcookie_registry_endpoint_help",
            default=u"If set and chefcookie will send usage data to endpoint",
        ),
        required=False,
    )
    domain_whitelist = schema.List(
        title=_("chefcookie_domain_whitelist_labels", default=u"Domain whitelist"),
        description=_(
            "chefcookie_domain_whitelist_labels_help",
            default=u"Insert a list of domains for which the banner should be used. Useful when we can visit a site with multiple domains",
        ),
        missing_value=[],
        default=[],
        value_type=schema.TextLine(),
        required=False,
    )
    analytics_id = schema.TextLine(
        title=_("chefcookie_analytics_id_label", default=u"Analytics Id"),
        description=_(
            "chefcookie_analytics_id_help",
            default=u"If set and the user has accepted the Analytics cookies, "
            "this id will be used to track the user. To enable this checkbox in "
            'the banner, you also need to add the "analytics" labels into '
            '"Technical cookies specific labels" field.',
        ),
        required=False,
    )
    matomo_id = schema.TextLine(
        title=_("chefcookie_matomo_id_label", default=u"Matomo Id"),
        description=_(
            "chefcookie_matomo_id_help",
            default=u"If set and the user has accepted the Matomo cookies, this id will be used to track the user.",
        ),
        required=False,
    )
    facebook_id = schema.TextLine(
        title=_("chefcookie_facebook_id_label", default=u"Facebook Id"),
        description=_(
            "chefcookie_facebook_id_help",
            default=u"If set and the user has accepted the Facebook cookies, this id will be used to track the user.",
        ),
        required=False,
    )

    hotjar_id = schema.TextLine(
        title=_("chefcookie_hotjar_id_label", default=u"HotJar Id"),
        description=_(
            "chefcookie_hotjar_id_help",
            default=u"If set and the user has accepted the HotJar cookies, this id will be used to track the user.",
        ),
        required=False,
    )

    linkedin_id = schema.TextLine(
        title=_("chefcookie_linkedin_id_label", default=u"LinkedIn Id"),
        description=_(
            "chefcookie_linkedin_id_help",
            default=u"If set and the user has accepted the LinkedIn cookies, this id will be used to track the user.",
        ),
        required=False,
    )

    only_technical_cookies = schema.Bool(
        title=_(
            "chefcookie_only_technical_cookies_label",
            default=u"Only technical cookies",
        ),
        description=_(
            "chefcookie_only_technical_cookies_help",
            default=u"Select if your website only provide technical cookies.",
        ),
        required=False,
    )

    policy_url = schema.SourceText(
        title=_("chefcookie_policy_url_label", default=u"Policy URL"),
        description=_(
            "chefcookie_policy_url_help",
            default="Insert the cookie policy page URL. One per each language in the website. "
            'This can be used in "Banner header" field as "{policy_url}" to '
            "dynamically replace it with the given URL.",
        ),
        default=u"{}",
        constraint=validate_cfg_json,
        required=False,
    )

    iframes_mapping = schema.List(
        title=_("chefcookie_iframes_mapping_labels", default=u"Iframes mapping"),
        description=_(
            "chefcookie_iframes_mapping_labels_help",
            default=u"Insert a list of mappings between a provider and a list of possible domains for their iframes. If the user blocks their cookies, the iframes will be blocked as well.",
        ),
        default=[],
        missing_value=[],
        value_type=schema.TextLine(),
        required=False,
    )
    links_mapping = schema.List(
        title=_("chefcookie_links_mapping_labels", default=u"Links mapping "),
        description=_(
            "chefcookie_links_mapping_labels_help",
            default=u"Insert a list of mappings between a provider and a list of possible links xpath selector for their anchor. If the user blocks their cookies, the provider will be blocked as well.",
        ),
        default=[],
        missing_value=[],
        value_type=schema.TextLine(),
        required=False,
    )


class IChefCookieSettingsLabels(Schema):
    header_labels = schema.SourceText(
        title=_("chefcookie_header_label", default=u"Banner header"),
        description=_(
            "chefcookie_header_help",
            default=u"Insert the text of the banner header. Once per each site "
            "languages. If you want to insert a link to the policy page, use "
            "the placeholder {policy_url}.",
        ),
        default=HEADER_LABELS,
        constraint=validate_cfg_json,
        required=True,
    )

    general_labels = schema.SourceText(
        title=_("chefcookie_general_labels", default=u"General labels"),
        description=_(
            "chefcookie_general_labels_help",
            default=u"",
        ),
        default=GENERAL_LABELS,
        constraint=validate_cfg_json,
        required=True,
    )

    technical_cookies_labels = schema.SourceText(
        title=_(
            "chefcookie_technical_cookies_labels",
            default=u"Technical cookies labels",
        ),
        description=_(
            "chefcookie_technical_cookies_labels_help",
            default=u"",
        ),
        default=TECHNICAL_COOKIES_LABELS,
        constraint=validate_cfg_json,
        required=False,
    )
    technical_cookies_specific_labels = schema.SourceText(
        title=_(
            "chefcookie_technical_cookies_specific_labels",
            default=u"Technical cookies specific labels",
        ),
        description=_(
            "chefcookie_technical_cookies_specific_labels_help",
            default=u"Labels for specific technical cookies.",
        ),
        default=TECHNICAL_COOKIES_SPECIFIC_LABELS,
        constraint=validate_cfg_json,
        required=True,
    )
    profiling_cookies_labels = schema.SourceText(
        title=_(
            "chefcookie_profiling_cookies_labels",
            default=u"Profiling cookies labels",
        ),
        description=_(
            "chefcookie_profiling_cookies_labels_help",
            default=u"",
        ),
        default=PROFILING_COOKIES_LABELS,
        constraint=validate_cfg_json,
        required=True,
    )

    profiling_cookies_specific_labels = schema.SourceText(
        title=_(
            "chefcookie_profiling_cookies_specific_labels",
            default=u"Profiling cookies specific labels",
        ),
        description=_(
            "chefcookie_profiling_cookies_specific_labels_help",
            default=u"Labels for specific providers. If the relative id/flag is set, this will enable the flag in the banner.",
        ),
        default=PROFILING_COOKIES_SPECIFIC_LABELS,
        constraint=validate_cfg_json,
        required=True,
    )


class IChefCookieSettings(IChefCookieSettingsConfigs, IChefCookieSettingsLabels):
    """"""
