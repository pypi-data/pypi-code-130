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
            dqjhw__hiu = set()
            wjy__dxted = list(self.context._get_attribute_templates(self.key))
            eob__diy = wjy__dxted.index(self) + 1
            for jyv__oraoc in range(eob__diy, len(wjy__dxted)):
                if isinstance(wjy__dxted[jyv__oraoc], numba.core.typing.
                    templates._OverloadAttributeTemplate):
                    dqjhw__hiu.add(wjy__dxted[jyv__oraoc]._attr)
            self._attr_set = dqjhw__hiu
        return attr_name in self._attr_set
