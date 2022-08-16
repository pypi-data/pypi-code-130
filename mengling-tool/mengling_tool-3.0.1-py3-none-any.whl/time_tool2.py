# -*- coding: UTF-8 -*-

import calendar
import re
import time
from datetime import datetime, timedelta, date

GS = "%Y-%m-%d %H:%M:%S"


# 日期转字符串
def date_str(date: datetime, gs="%Y-%m-%d"):
    return date.strftime(gs)


# 字符串转日期
def str_date(txt, min_havepro_num=3):
    ts = re.findall('\d{2}', txt)
    assert len(ts) > min_havepro_num, '提取数量少于最小项数目!'
    year = ts.pop(0) + ts.pop(0)
    month = ts.pop(0)
    day = ts.pop(0)
    h = ts.pop(0) if len(ts) > 0 else '00'
    m = ts.pop(0) if len(ts) > 0 else '00'
    s = ts.pop(0) if len(ts) > 0 else '00'
    return datetime.strptime(f'{year}-{month}-{day} {h}:{m}:{s}', GS)


# 下一天,可变动数值
def dateNext(txtdate: datetime or str, dn, hn=0, mn=0, sn=0, min_havepro_num=3):
    if type(txtdate) is str: txtdate = str_date(txtdate, min_havepro_num=min_havepro_num)
    dd = txtdate + timedelta(days=dn, hours=hn, minutes=mn, seconds=sn)
    return dd


# 时间戳转日期
def stamp_date(stamp: int):
    timeArray = time.localtime(stamp)  # 把时间戳转化为时间: 1479264792 to 2016-11-16 10:53:12
    txt = time.strftime(GS, timeArray)
    return str_date(txt, 6)


# 日期转时间戳
def date_stamp(date: datetime) -> int:
    # 转换为时间戳
    stamp = round(time.mktime(date.timetuple()))
    return stamp


# 获取当前时间
def getNowDatetime(next_num=0):
    return dateNext(datetime.now(), dn=next_num, min_havepro_num=6)


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
def getTimeSection(txtdate: datetime or str, forward: int, backward: int, ifgetdate=False, min_havepro_num=3,
                   re_gs='%Y-%m-%d') -> list:
    if type(txtdate) is str: txtdate = str_date(txtdate, min_havepro_num=min_havepro_num)
    results = list()
    for i in range(-forward, backward + 1):
        tempdd = dateNext(txtdate, i)
        if ifgetdate:
            results.append(tempdd)
        else:
            results.append(date_str(tempdd, re_gs))
    return results


# 获取时间区间
def getDateList(start_txtdate: datetime or str, end_txtdate: datetime or str, min_havepro_num=3, gs='%Y-%m-%d',
                interval_day=1) -> list:
    txt_list = list()
    if type(start_txtdate) is str: start_txtdate = str_date(start_txtdate, min_havepro_num=min_havepro_num)
    if type(end_txtdate) is str: end_txtdate = str_date(end_txtdate, min_havepro_num=min_havepro_num)
    txt_list.append(start_txtdate.strftime(gs))
    while start_txtdate < end_txtdate:
        start_txtdate += timedelta(days=interval_day)
        txt_list.append(start_txtdate.strftime(gs))
    # 包含最后一天
    return txt_list


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
def getLastDay(year, mon, ifre_str=False, gs='%Y-%m-%d'):
    firstDayWeekDay, monthRange = calendar.monthrange(year, mon)
    d = date(year=year, month=mon, day=monthRange)
    if ifre_str:
        return date_str(d, gs=gs)
    else:
        return d


# 秒数转时长
def secondToTime(s0: int, ifre_str=True) -> (int, int, int) or str:
    m, s = divmod(s0, 60)
    h, m = divmod(m, 60)
    if ifre_str:
        return "%02d时%02d分%02d秒" % (h, m, s)
    else:
        return h, m, s


if __name__ == '__main__':
    print(getTimeSection('20200121', 5, 3))
