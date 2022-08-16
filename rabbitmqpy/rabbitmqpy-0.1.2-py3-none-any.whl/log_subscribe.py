# coding:utf-8

import os
import json
import time
import traceback
from datetime import datetime, timedelta
from .subscribe import Subscriber

noinput_time = 600
retry_times = 3

class LogSubscriber(Subscriber):
    """订阅者
    接收日志消息
    """
    def __init__(self, *args, **kwargs):
        self.file_pool = dict()
        Subscriber.__init__(self, *args, **kwargs)

    def open_session(self, filepath, now_time):
        """打开一个文件对话, 更新调用时间"""
        if self.file_pool.get(filepath) is None:
            self.file_pool[filepath] ={
                    "f": open(filepath, "at"),
                    "utime": now_time}
        else:
            self.file_pool[filepath]["utime"] = now_time
        return self.file_pool[filepath]["f"]

    def close_session(self, filepath):
        """关闭一个文件对话"""
        if self.file_pool.get(filepath) is not None:
            try:
                file_session = self.file_pool.pop(filepath)
                file_session["f"].close()
            except:
                pass

    def reopen_session(self, filepath, now_time):
        """重新打开文件对话"""
        self.close_session(filepath)
        self.open_session(filepath, now_time)

    def close_longtime_noinput(self, now_time):
        """关闭长时间无输入的文件"""
        file_pool_filter = lambda x: now_time - self.file_pool[x]["utime"] > noinput_time
        out_of_oninput = list(filter(file_pool_filter, self.file_pool.keys()))
        for i in out_of_oninput:
            self.close_session(i)

    def __del__(self):
        for k in self.file_pool:
            self.close_session(k)

    def check_file_create_time(self, filepath, backup, now_time):
        """检查文件创建时间"""
        filectime = os.path.getctime(filepath)
        f_ctime = time.strptime(time.ctime(filectime))
        now = time.strptime(time.ctime(now_time))
        if now.tm_mday != f_ctime.tm_mday or now.tm_mon != f_ctime.tm_mon or now.tm_year != f_ctime.tm_year:
            self.close_session(filepath)
            new_filepath = '%s.%s.log' % (filepath, time.strftime("%Y-%m-%d", f_ctime))
            os.rename(filepath, new_filepath)
            self.delete_expire_file(filepath, backup)

    def delete_expire_file(self, filepath, backup):
        """删除过期的日志文件"""
        now = datetime.now()
        expire_datetime = now - timedelta(days=backup)
        while True:
            expire_datetime = expire_datetime - timedelta(days=1)
            expire_filepath = '%s.%s.log' % (filepath, expire_datetime.strftime("%Y-%m-%d"))
            if os.path.isfile(expire_filepath):
                os.remove(expire_filepath)
            else:
                break

    def write_logs(self, filepath, f, logs, now_time):
        """写日志"""
        for _ in range(retry_times):
            try:
                f.write("f:%s|%s\n" % (len(self.file_pool), logs))
                f.flush()
                break
            except:
                print(traceback.format_exc())
                self.reopen_session(filepath, now_time)

    def on_message(self, chan, method_frame, header_frame, body, userdata=None):
        """运行订阅任务"""
        try:
            # 解析数据
            json_data  = body.decode("utf-8")
            _json_data = json.loads(json_data)
            filepath   = _json_data['filepath']
            backup     = _json_data['backup']
            logs       = _json_data['logs']

            # 校验数据
            if not os.path.isabs(filepath):
                print("路径参数filepath必须是合法的绝对路径:%s" % filepath)
                return
            if not isinstance(backup, int):
                print("备份数量参数backup不是合法参数:%s" % backup)
                return
            if not logs:
                print("没有日志信息")
                return

            now_time = time.time()

            # 判断文件夹是否存在，不存在则创建
            folder = os.path.dirname(filepath)
            if not os.path.exists(folder):
                os.makedirs(folder)

            if not os.path.isfile(filepath):
                f = self.open_session(filepath, now_time)
            else:
                # 如果是新日期，则关闭旧日志文件，打开新日志文件
                self.check_file_create_time(filepath, backup, now_time)
                # 获取session
                f = self.open_session(filepath, now_time)

            # 写日志
            self.write_logs(filepath, f, logs, now_time)

            # 关闭长时间无日志的文件对话
            self.close_longtime_noinput(now_time)

        except Exception:
            print(traceback.format_exc())


if __name__=='__main__':
    amqp_url = 'amqp://10.12.3.162:32037'
    receive_log = LogSubscriber(
            amqp_url,
            'imlf_mqlog_test',
            'direct',
            'imlf_mqlog_queue_test',
            routing_key='imlf_mqlog_key_test'
            )
    receive_log.start()
