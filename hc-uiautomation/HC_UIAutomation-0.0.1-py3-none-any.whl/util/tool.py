import time
from datetime import datetime
import os

def currentDate():
    date = time.localtime()
    # 构造今天的日期字符串
    today = str(date.tm_year) + "-" + str(date.tm_mon) + "-" + str(date.tm_mday)
    return today


def currentTime():
    timeStr = datetime.now()
    # 构造当前时间字符串
    now = timeStr.strftime('%H-%M-%S')
    return now

def createDir():
    # 获得当前文件所在目录绝对路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\screenshot'
    today = currentDate()
    # 构造以今天日期命名的目录的绝对路径
    date_dir = os.path.join(base_dir, today)
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    if not os.path.exists(date_dir):
        # 如果已今天日期命名的目录不存在则创建
        os.mkdir(date_dir)
    # # 获得当前的时间字符串
    # now = currentTime()
    # # 构造以当前时间命名的目录的绝对路径
    # time_dir = os.path.join(date_dir, now)
    # if not os.path.exists(time_dir):
    #     # 如果已当前时间命名的目录不存在则创建
    #     os.mkdir(time_dir)
    return date_dir


if __name__ == "__main__":
    createDir()


