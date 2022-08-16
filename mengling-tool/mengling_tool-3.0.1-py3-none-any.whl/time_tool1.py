import calendar
import time
from datetime import datetime, timedelta, date

# "%Y/%m/%d %H:%M:%S"
GS = "%Y%m%d"


# 日期转字符串
def datetime_str(datetime, gs=None):
    gs = GS if gs is None else gs
    return datetime.strftime(gs)


# 字符串转日期
def str_datetime(string, gs=None):
    gs = GS if gs is None else gs
    return datetime.strptime(string, gs)


# 下一天,可变动数值
def datetimeNext(datetime, dn, hn=0, mn=0, sn=0,
                 gs=None, returnstr=False):
    gs = GS if gs is None else gs
    dd = datetime + timedelta(days=dn, hours=hn, minutes=mn, seconds=sn)
    if returnstr:
        return datetime_str(dd, gs)
    else:
        return dd


# 下一天,可变动数值
def strNext(string, dn, hn=0, mn=0, sn=0, gs=None, returnstr=False):
    gs = GS if gs is None else gs
    datetime = str_datetime(string, gs)
    return datetimeNext(datetime, dn, hn=hn, mn=mn, sn=sn, gs=gs, returnstr=returnstr)


# 时间戳转日期
def stamp_datetime(stamp, gs="%Y/%m/%d %H:%M:%S"):
    timeArray = time.localtime(stamp)  # 把时间戳转化为时间: 1479264792 to 2016-11-16 10:53:12
    string = time.strftime(gs, timeArray)
    return str_datetime(string, gs)


# 日期转时间戳
def datetime_stamp(date, ifinstr=False):
    if not ifinstr:
        string = datetime_str(date)
    else:
        string = date
    # 将其转换为时间数组
    timearray = time.strptime(string, GS)
    # 转换为时间戳
    return int(time.mktime(timearray))


# 获取当前时间
def getNowDatetime(returnstr=False, gs=None):
    if returnstr:
        return datetime_str(datetime.now(), gs=gs)
    else:
        return datetime.now()


# 获取时间戳
def getNowStamp_f():
    return time.time()


# 运行时间显示装饰器
def runTimeFunc(func):
    def temp(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print('方法', func.__name__, '运行时间：', round(time.time() - start, 4), '秒')
        return result

    return temp


# 获取时间区间
def getTimeSection(string, forward: int, backward: int, ifgetdate=False, gs=GS):
    dd = str_datetime(string, gs)
    results = list()
    for i in range(-forward, backward + 1):
        tempdd = datetimeNext(dd, i)
        if ifgetdate:
            results.append(tempdd)
        else:
            results.append(datetime_str(tempdd, gs))
    return results


# 获取时间区间
def getDateList(start_date, end_date, gs='%Y-%m-%d'):
    date_list = []
    start_date = datetime.strptime(start_date, gs)
    end_date = datetime.strptime(end_date, gs)
    date_list.append(start_date.strftime(gs))
    while start_date < end_date:
        start_date += timedelta(days=1)
        date_list.append(start_date.strftime(gs))
    # 包含最后一天
    return date_list


# 输出等待
def printWait(sleeptime):
    for i in range(sleeptime):
        print('\r剩余时间：%s 秒     ' % (sleeptime - i), end='')
        time.sleep(1)


# 计算年龄 周岁
def calculate_age(year, mon, day):
    today = date.today()
    return today.year - int(year) - ((today.month, today.day) < (int(mon), int(day)))


# 休息输出通知函数
def sleePrintTime(sleeptime: int, qz_txt='剩余时间'):
    for i in range(sleeptime):
        print(f'\r{qz_txt}：{sleeptime - i} 秒     ', end='')
        time.sleep(1)


# 获取某月最后一天
def getLastDay(year, mon, returnstr=False, gs=None):
    firstDayWeekDay, monthRange = calendar.monthrange(year, mon)
    d = date(year=year, month=mon, day=monthRange)
    if returnstr:
        return datetime_str(d, gs=gs)
    else:
        return d


# 秒数转时长
def secondToTime(s0: int, ifstr=True) -> (int, int, int) or str:
    m, s = divmod(s0, 60)
    h, m = divmod(m, 60)
    if ifstr:
        return "%02d时%02d分%02d秒" % (h, m, s)
    else:
        return (h, m, s)


if __name__ == '__main__':
    print(getTimeSection('20200121', 5, 3))
