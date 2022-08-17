# -*- coding: utf-8 -*-
from eea.facetednavigation.widgets import ViewPageTemplateFile
from eea.facetednavigation.widgets.select.widget import Widget as SelectWidget
from eea.facetednavigation.widgets.select.interfaces import ISelectSchema

from Products.CMFPlone.utils import safe_unicode
from zope.i18n import MessageFactory

_ = MessageFactory('collective.z3cform.select2')


def compare_lowercase(a, b):
    a = safe_unicode(a)
    b = safe_unicode(b)
    return a.lower() == b.lower()


class ISelect2Schema(ISelectSchema):
    """ """


class Widget(SelectWidget):
    """ Widget
    """

    # Widget properties
    widget_type = 'select2'
    widget_label = _('Select2')

    index = ViewPageTemplateFile('templates/select2.pt')

    @property
    def default(self):
        """ Get default values
        """
        default = super(SelectWidget, self).default
        if not default:
            return []

        if isinstance(default, (str, unicode)):
            default = [default, ]

        return default

    def selected(self, key):
        """ Return True if key in self.default
        """
        default = self.default
        if not default:
            return False

        for item in default:
            if compare_lowercase(key, item):
                return True

        return False
