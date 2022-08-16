from zope.interface import Interface


class INodePlaceholder(Interface):
    """
    Provide correct placeholder for a node we need to hide due to GDPR
    """

    def transform_node(self, provider, node):
        """
        @param provider: the provider name
        @param node: the lxml node we need to transform
        @return: the modified anchor and the reative placeholder
        """
