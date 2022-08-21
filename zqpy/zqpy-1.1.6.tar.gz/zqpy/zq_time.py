import time
from datetime import datetime
from threading import Timer
import zq_log

def time_format(mFormat, mTime = None):
    ''' 时间格式化 字符串 '''
    if mTime == None:
        mTime = time.localtime()
    return time.strftime(mFormat, mTime)

def time_file_time_str(mTime = None):
    ''' 年_月_日_时_分_秒 字符串 '''
    return time_format('%Y_%m_%d_%H_%M_%S',mTime)

def time_long_time_str(mTime = None):
    ''' 年-月-日 时:分:秒 字符串 '''
    return time_format('%Y-%m-%d %H:%M:%S',mTime)
    
def time_short_time_str(mTime = None):
    ''' 年-月-日 字符串 '''
    return time_format('%Y-%m-%d',mTime)

def time_local_time():
    ''' 当前本地时间 '''
    return time.localtime()

def time_int():
    ''' 当前时间转int '''
    return int(time.time())

def time_sleep(sleep = 0):
    ''' 时间停留 '''
    time.sleep(sleep)

def time_format_by_timestamp(timeStamp, formatStr = "%Y-%m-%d %H:%M:%S"):
    ''' 时间戳转时间字符串格式 '''
    timeArray = time.localtime(int(timeStamp))
    return time_format(formatStr, timeArray)

def time_day_zero(date):
    """根据日期获取某天凌晨时间"""
    if not date:
        return 0
    date_zero = datetime.now().replace(year=date.year, month=date.month,
                                                day=date.day, hour=0, minute=0, second=0)
    date_zero_time = int(time.mktime(date_zero.timetuple())) * 1000
    return date_zero_time

def time_curr_day_zero(isSecond):
    '''
    根据日期获取当天凌晨时间
    :param: isSecond 是否是秒
    '''
    # 今天的日期
    today_date = datetime.now().date()
    # 今天的零点
    ms = time_day_zero(today_date) 
    if isSecond:
        return int(ms/1000)
    return ms

def time_curr_time():
    ''' 当前时间 datetime '''
    return datetime.now()

def time_next_day_time(year=None, month=None, day=None, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
    ''' 获取下一天的当前时间 '''
    return time_curr_time()+datetime.timedelta(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=microsecond, tzinfo=tzinfo)

def time_yesterday(timedelta=-1): 
    '''向前天'''
    yesterday = datetime.date.today() + datetime.timedelta(timedelta)
    return yesterday

def time_str_is_same_day(source_date, target_date=None):
    '''
    判断字符串是否是同一天(支持仅年月日)
    source_date:年-月-日 时:分:秒
    target_date:年-月-日 时:分:秒
    '''
    source_date = source_date.replace('/', '-')
    target_date = target_date.replace('/', '-') if target_date else None
    is_same_day = False
    try:
        date_format = '%Y-%m-%d'
        if len(source_date.split(' ')) > 1:
            date_format = '%Y-%m-%d %H:%M:%S'
        target_date = target_date if target_date else time.strftime(date_format, time.localtime(time.time()))
        source_date = datetime.strptime(source_date, date_format).date()
        target_date = datetime.strptime(target_date, date_format).date()
        is_same_day = source_date == target_date
    except Exception as e:
        zq_log.log_debug('time_str_is_same_day error: %s'%str(e))
    return is_same_day

def time_str_to_date(source_date):
    '''
    字符串时间转时间data(支持仅年月日)
    source_date:年-月-日 时:分:秒
    '''
    source_date = source_date.replace('/', '-')
    date_format = '%Y-%m-%d'
    if len(source_date.split(' ')) > 1:
        date_format = '%Y-%m-%d %H:%M:%S'
    return datetime.strptime(source_date, date_format)

def time_compare_date(source_date, target_date=None):
    '''
    判断时间字符串前一个是否比后一个大(支持仅年月日)
    source_date:年-月-日 时:分:秒
    target_date:年-月-日 时:分:秒
    '''
    source_date = source_date.replace('/', '-')
    target_date = target_date.replace('/', '-') if target_date else None
    compare = 0
    try:
        date_format = '%Y-%m-%d'
        if len(source_date.split(' ')) > 1:
            date_format = '%Y-%m-%d %H:%M:%S'
        target_date = target_date if target_date else time.strftime(date_format, time.localtime(time.time()))
        source_date = datetime.strptime(source_date, date_format).timestamp()
        target_date = datetime.strptime(target_date, date_format).timestamp()
        compare = source_date - target_date
    except Exception as e:
        zq_log.log_debug('time_str_is_same_day error: %s'%str(e))
    return compare

