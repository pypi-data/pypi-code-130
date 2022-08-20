from telecms_bridge_base.fields import BooleanField
from telecms_bridge_base.filters.filter import Filter


class BooleanFilter(Filter):
    field_class = BooleanField
