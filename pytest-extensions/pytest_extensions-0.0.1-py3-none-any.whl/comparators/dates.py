from datetime import datetime, date, timedelta, tzinfo, timezone, time

from .types import TypeComparator


a_date = TypeComparator(date)
a_time = TypeComparator(time)
a_datetime = TypeComparator(datetime)
a_timedelta = TypeComparator(timedelta)
a_tzinfo = TypeComparator(tzinfo)
a_timezone = TypeComparator(timezone)


#TODO:
# a_timestamp
# a_formatted_date
# an_iso_date
# an_iso_datetime
# ...
