# -*- coding: utf-8 -*-
from lxml import etree
from plone import api
from plone.registry.interfaces import IRegistry
from plone.transformchain.interfaces import ITransform
from redturtle.chefcookie.defaults import domain_allowed
from redturtle.chefcookie.interfaces import IChefCookieSettings
from redturtle.chefcookie.interfaces import IRedturtleChefcookieLayer
from redturtle.chefcookie.transformers import INodePlaceholder
from repoze.xmliter.utils import getHTMLSerializer
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component.interfaces import ComponentLookupError
from zope.interface import implementer
from zope.interface import Interface

import logging
import six

if six.PY2:
    from urlparse import urlparse
else:
    from urllib.parse import urlparse


logger = logging.getLogger(__name__)


@implementer(ITransform)
@adapter(Interface, IRedturtleChefcookieLayer)  # any context, any request
class ChefcookieIframeTransform(object):

    order = 8887  #  just one less than collective.lazysizes

    def __init__(self, published, request):
        self.published = published
        self.request = request
        self.chefcookie_registry_record = None

    def get_config_name(self, src):
        """
        if the src matches configured domains, return the config name
        """
        if not src:
            return ""
        iframes_mapping = self.chefcookie_registry_record.iframes_mapping
        for mapping in filter(bool, iframes_mapping):
            name, domains = mapping.split("|")
            if not domains:
                continue
            domains = domains.split(",")
            for domain in domains:
                if domain.strip() in src:
                    return name
        return ""

    def transform_iframe(self, iframe):
        src = iframe.attrib.get("src")
        provider = self.get_config_name(src=src)
        if not provider:
            # no match, no need to mask it
            return

        adapter = self.get_transform_adapter(
            provider=provider, interface=INodePlaceholder
        )
        if adapter:
            adapter.transform_node(provider=provider, node=iframe)

    def transformIterable(self, result, encoding):
        # we pass through this code for every call client made to server,
        # so also for resource.
        try:
            registry = getUtility(IRegistry)
        except ComponentLookupError:
            # as far as i can see sometimes this transform is called but it's
            # not able to get the utility. This simply hides useless exception
            # in log
            return
        if not registry:
            # and sometimes getUtility return None... we need to skip this as
            # well
            return
        content_type = self.request.response.getHeader("Content-Type")
        if not content_type or not content_type.startswith("text/html"):
            return

        if not self.published or self.published.__name__ in ["edit", "@@edit"]:
            return result

        try:
            self.chefcookie_registry_record = registry.forInterface(IChefCookieSettings)
        except KeyError:
            return

        if not self.chefcookie_registry_record.enable_cc and domain_allowed(  # noqa
            self.chefcookie_registry_record.domain_whitelist,
            urlparse(self.request.get("URL")).netloc,
        ):
            return

        try:
            result = getHTMLSerializer(result)
        except (AttributeError, TypeError, etree.ParseError):
            return
        for iframe in result.tree.xpath("//iframe"):
            self.transform_iframe(iframe)

        path = "//a[@class='{}']"
        links_mapping = self.chefcookie_registry_record.links_mapping

        for configuration in filter(bool, links_mapping):
            provider, provider_class = configuration.split("|")
            for anchor in result.tree.xpath(path.format(provider_class)):
                adapter = self.get_transform_adapter(
                    provider=provider, interface=INodePlaceholder
                )
                if adapter:
                    adapter.transform_node(provider=provider, node=anchor)
        return result

    def get_transform_adapter(self, provider, interface):
        adapter = queryMultiAdapter(
            (api.portal.get(), self.request),
            interface=interface,
            name="transform.{}".format(provider),
        )

        adapter = adapter or getMultiAdapter(
            (api.portal.get(), self.request), interface=interface
        )
        return adapter
