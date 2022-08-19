import datetime
from lpack import utils


# a = utils.TimePot.date_to_char('M')
a = '2022-05-13 15:23:00'

b = utils.TimePot.char_to_date(a, 's')
print(type(b))
print(utils.TimePot.date_diff(b))
print(utils.TimePot.date_to_stamp(b))