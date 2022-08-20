from telecms_bridge_base.fields import CharField
from telecms_bridge_base.filters.filter import Filter


class CharFilter(Filter):
    field_class = CharField
