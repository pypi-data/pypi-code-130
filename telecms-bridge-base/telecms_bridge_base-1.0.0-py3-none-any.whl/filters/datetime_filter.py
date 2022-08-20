
from telecms_bridge_base.fields.datetime import DateTimeField
from telecms_bridge_base.filters.filter import Filter


class DateTimeFilter(Filter):
    field_class = DateTimeField
