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
            pef__mdcmg = set()
            get__dvn = list(self.context._get_attribute_templates(self.key))
            apncq__mxoso = get__dvn.index(self) + 1
            for lwfb__juf in range(apncq__mxoso, len(get__dvn)):
                if isinstance(get__dvn[lwfb__juf], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    pef__mdcmg.add(get__dvn[lwfb__juf]._attr)
            self._attr_set = pef__mdcmg
        return attr_name in self._attr_set
