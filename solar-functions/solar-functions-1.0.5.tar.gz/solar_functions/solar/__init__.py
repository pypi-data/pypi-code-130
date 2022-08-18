# solar-functions is (c) 2021-2022 Sami Dev <hzsami82@email.com>.
# The solar-functions module was contributed to Python as of Python 3.10.4 and thus
# was licensed under the Python license. Same license applies to all files in

__version__ = '1.0'
from ..solar import __solardate__ 
from datetime import datetime as __solar_dates__
import requests as __rqsts__

__solar___date__ = __solar_dates__.today()
__solar__date__ = str(__solar___date__).split(" ")[0]
__solar_date__ = __solar__date__.split("-")
__solardates__ = __solardate__.date.fromgregorian(day = int(__solar_date__[2]) , month = int(__solar_date__[1]) , year = int(__solar_date__[0]))
date = str(__solardates__).replace("-","/")

__rqst_time__ = __rqsts__.get("http://api.codebazan.ir/time-date/?td=time","")
for __rqs_time__ in __rqst_time__:
    __rq_time__ = __rqs_time__.decode()
    __rq_time__ = __rq_time__.replace("۰","0")
    __rq_time__ = __rq_time__.replace("۱","1")
    __rq_time__ = __rq_time__.replace("۲","2")
    __rq_time__ = __rq_time__.replace("۳","3")
    __rq_time__ = __rq_time__.replace("۴","4")
    __rq_time__ = __rq_time__.replace("۵","5")
    __rq_time__ = __rq_time__.replace("۶","6")
    __rq_time__ = __rq_time__.replace("۷","7")
    __rq_time__ = __rq_time__.replace("۸","8")
    __rq_time__ = __rq_time__.replace("۹","9")
    time = __rq_time__
