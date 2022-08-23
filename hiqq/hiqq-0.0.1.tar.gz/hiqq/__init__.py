import json
import requests


class Robot:
    """
    QQ python

    """

    def __init__(self, url, token, qq_number):
        self.url = url
        self.qq_number = qq_number
        self.token = token

    def command(self, name):
        url = self.url
        data = {"type": "Q0003",
                "data": {},
                }
        r = requests.post(url=url, json=data)
        print(r.json())

    def post_(self, data_):
        data_ = json.dumps(data_)
        r = requests.post(url=self.url, data=data_)

        return r.json()

    def say(self, acceptwxid, msg):
        type_ = "Q0001"
        data_ = {
            "type": f"{type_}",
            "data": {
                "wxid": f"{acceptwxid}",
                "msg": f"{msg}"}
        }

        return self.post_(type_, data_)

    def version(self):
        f = "Api_GetVer"
        data_ = {
            "function": f"{f}",  # 要调用的函数英文名(查看右侧API列表)
            "token": f"{self.token}",  # 后台设置的token
            "params": {
                "c1": "363751070",  # 参数1，要使用的机器人QQ
                "c2": "2",  # 参数2，消息类型，2为群，以此类推...
                "c3": "320562077",  # 参数3，要发送的群号，以此类推...
                "c4": "",  # 参数4，要发送的QQ，此处发的是群，所以这个要留空，以此类推...
                "c5": "你好，测试一下"  # 参数5，要发送的消息内容，以此类推...
            }
        }

        return self.post_(data_)

    def get_time_stamp(self):
        f = "Api_GetTimeStamp"
        data_ = {
            "function": f"{f}",  # 要调用的函数英文名(查看右侧API列表)
            "token": f"{self.token}",  # 后台设置的token
            "params": {
                "c1": "363751070",  # 参数1，要使用的机器人QQ
                "c2": "2",  # 参数2，消息类型，2为群，以此类推...
                "c3": "320562077",  # 参数3，要发送的群号，以此类推...
                "c4": "",  # 参数4，要发送的QQ，此处发的是群，所以这个要留空，以此类推...
                "c5": "你好，测试一下"  # 参数5，要发送的消息内容，以此类推...
            }
        }
        return self.post_(data_)

    def send_msg(self, msgtype, qq_group_number="", qq_number="", msg_content="QQ 2696047693"):
        f = "Api_SendMsg"
        data_ = {
            "function": f"{f}",  # 要调用的函数英文名(查看右侧API列表)
            "token": f"{self.token}",  # 后台设置的token
            "params": {
                "c1": f"{self.qq_number}",  # 参数1，要使用的机器人QQ
                "c2": f"{msgtype}",  # 参数2，消息类型，2为群，以此类推...
                "c3": f"{qq_group_number}",  # 参数3，要发送的群号，以此类推...
                "c4": f"{qq_number}",  # 参数4，要发送的QQ，此处发的是群，所以这个要留空，以此类推...
                "c5": f"{msg_content}"  # 参数5，要发送的消息内容，以此类推...
            }
        }
        print(data_)
        return self.post_(data_)

    def receive(self, token):
        data = {"token": f"{token}"}

        url = "http://114.116.54.227:8005/sqlread"
        r = requests.post(url=url, data=data)
        return r.json()

    def receive_msg_clear(self, token):
        data = {"token": f"{token}"}

        url = "http://114.116.54.227:8005/sqlclear"
        r = requests.post(url=url, data=data)
        return r.json()

    def get_nick_name(self,other_qq):
        f = "Api_GetNick"
        data_ = {
            "function": f"{f}",  # 要调用的函数英文名(查看右侧API列表)
            "token": f"{self.token}",  # 后台设置的token
            "params": {
                "c1": f"{self.qq_number}",  # 参数1，要使用的机器人QQ
                "c2": f"{other_qq}",  # 参数2，消息类型，2为群，以此类推...
                # "c3": f"{qq_group_number}",  # 参数3，要发送的群号，以此类推...
                # "c4": f"{qq_number}",  # 参数4，要发送的QQ，此处发的是群，所以这个要留空，以此类推...
                # "c5": f"{msg_content}"  # 参数5，要发送的消息内容，以此类推...
            }
        }
        print(data_)
        return self.post_(data_)

    def get_friend_list(self):
        f = "Api_GetFriendList"
        data_ = {
            "function": f"{f}",  # 要调用的函数英文名(查看右侧API列表)
            "token": f"{self.token}",  # 后台设置的token
            "params": {
                "c1": f"{self.qq_number}",  # 参数1，要使用的机器人QQ
                # "c2": f"{other_qq}",  # 参数2，消息类型，2为群，以此类推...
                # "c3": f"{qq_group_number}",  # 参数3，要发送的群号，以此类推...
                # "c4": f"{qq_number}",  # 参数4，要发送的QQ，此处发的是群，所以这个要留空，以此类推...
                # "c5": f"{msg_content}"  # 参数5，要发送的消息内容，以此类推...
            }
        }
        print(data_)
        return self.post_(data_)

    def get_group_list(self):
        f = "Api_GetGroupList"
        data_ = {
            "function": f"{f}",  # 要调用的函数英文名(查看右侧API列表)
            "token": f"{self.token}",  # 后台设置的token
            "params": {
                "c1": f"{self.qq_number}",  # 参数1，要使用的机器人QQ
                # "c2": f"{other_qq}",  # 参数2，消息类型，2为群，以此类推...
                # "c3": f"{qq_group_number}",  # 参数3，要发送的群号，以此类推...
                # "c4": f"{qq_number}",  # 参数4，要发送的QQ，此处发的是群，所以这个要留空，以此类推...
                # "c5": f"{msg_content}"  # 参数5，要发送的消息内容，以此类推...
            }
        }
        print(data_)
        return self.post_(data_)


    def help(self):
        str = """
        QQ 2696047693[puthonnic]
        
        QQ群:769409487
        
        Software is like sex –– it's better when it's free.by Linus Torvalds.
        开源是一件很cool的事情。给别人看自己写的代码，全世界不同地方的人来用自己写的软件，难道不是很cool吗
        我现在就是做一件非常酷的事情

        
        
        感谢 Daen
        
        
        """
        print(str)


class Constant:
    Callback_Events = {
        "注入成功": "D0001",
        "登录成功": "D0002",
        "收到消息": "D0003"
                ""
    }

    qqmusicapp = "wx5aa333606550dfd5"
    neteasymusicapp = "wx8dd6ecd81906fd84"
    kugoumysciapp = "wx79f2c4418704b4f8"
