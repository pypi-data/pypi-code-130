"""
Helper functions and classes to simplify Template Generation
for Bodo classes.
"""
import numba
from numba.core.typing.templates import AttributeTemplate


class OverloadedKeyAttributeTemplate(AttributeTemplate):
    _attr_set = None

    def _is_existing_attr(self, attr_name):
        if self._attr_set is None:
            wfyu__bhyk = set()
            xal__mivxk = list(self.context._get_attribute_templates(self.key))
            miycf__ooi = xal__mivxk.index(self) + 1
            for nze__zvm in range(miycf__ooi, len(xal__mivxk)):
                if isinstance(xal__mivxk[nze__zvm], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    wfyu__bhyk.add(xal__mivxk[nze__zvm]._attr)
            self._attr_set = wfyu__bhyk
        return attr_name in self._attr_set
