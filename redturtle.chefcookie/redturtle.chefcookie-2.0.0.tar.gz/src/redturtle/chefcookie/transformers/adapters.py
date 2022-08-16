from redturtle.chefcookie.defaults import anchor_placeholder
from redturtle.chefcookie.transformers import INodePlaceholder
from zope.component import adapter
from zope.interface import implementer, Interface
from lxml import html
from redturtle.chefcookie.defaults import iframe_placeholder

import logging

logger = logging.getLogger(__name__)


@adapter(Interface, Interface)
@implementer(INodePlaceholder)
class DefaultPlaceholder(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def placeholder(self, provider):
        return iframe_placeholder(name=provider).prettify()

    def transform_node(self, provider, node):
        src = node.attrib.get("src")
        node.attrib.pop("src")
        node.set("data-cc-src", src)
        node.set("data-cc-name", provider)
        node.set("hidden", "true")
        placeholder = html.fromstring(self.placeholder(provider=provider))
        node.addprevious(placeholder)
        return


@adapter(Interface, Interface)
@implementer(INodePlaceholder)
class TwitterPlaceholder(DefaultPlaceholder):
    def placeholder(self, provider):
        return anchor_placeholder(provider).prettify()

    def transform_node(self, provider, node):
        """ """
        href = node.attrib.get("href")
        node.attrib.pop("href")
        node.set("data-cc-name", provider)
        node.set("data-cc-href", href)
        node.set("hidden", "true")

        twitter = node.getnext()
        src = twitter.attrib.get("src")
        twitter.attrib.pop("src")
        # twitter.set("data-cc-name", provider)
        twitter.set("data-cc-src", src)
        twitter.set("hidden", "true")
        node.addprevious(html.fromstring(self.placeholder(provider=provider)))


@adapter(Interface, Interface)
@implementer(INodePlaceholder)
class RecaptchaPlaceholder(DefaultPlaceholder):
    def transform_node(self, provider, node):
        """
        recaptcha generates an iframe in noscript tag, and the other one is
        loaded with the script
        """
        super(RecaptchaPlaceholder, self).transform_node(provider, node)

        # now disable the script
        for script in node.xpath(
            "//script[contains(@src, 'https://www.google.com/recaptcha/api.js')]"
        ):
            src = script.attrib.get("src")
            script.attrib.pop("src")
            script.set("data-cc-src", src)
        recaptcha_divs = node.xpath("//div[@class='g-recaptcha']")
        if recaptcha_divs:
            recaptcha_divs[0].addnext(
                html.fromstring(self.placeholder(provider=provider))
            )
