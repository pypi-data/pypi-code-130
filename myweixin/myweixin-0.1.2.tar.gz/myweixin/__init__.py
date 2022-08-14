import time
from . import information
import requests


# url = "http://127.0.0.1:7777/DaenWxHook/httpapi/?wxid=wxid_at1vbqt6zgg922"
# data = {"type": "Q0003",
#         "data": {},
#         }
# r = requests.post(url=url, json=data)
# print(r.json())


class Robot:
    """
    weixin python

    """

    def __init__(self, url, wxid):
        self.url = url
        self.wxid = wxid

    def command(self, name):
        url = self.url
        data = {"type": "Q0003",
                "data": {},
                }
        r = requests.post(url=url, json=data)
        print(r.json())

    def post_(self, type_, data_):
        url = self.url

        r = requests.post(url=url, json=data_, params={"wxid": f"{self.wxid}"})
        # print(r.json())
        return r.json()

    def say(self, acceptwxid, msg):
        type_ = "Q0001"
        data_ = {"wxid": f"{acceptwxid}",
                 "msg": f"{msg}"}

        self.post_(type_, data_)

    def get_friend_list(self):
        type_ = "Q0005"
        data_ = {"type": f"{type_}",
                 "data": {"type": "1"},
                 }

        return self.post_(type_, data_)

    def get_group_chat(self):
        type_ = "Q0006"
        data_ = {"type": f"{type_}",
                 "data": {"type": "1"},
                 }

        return self.post_(type_, data_)

    def send_music_sharing(self, wxid, name, author, app, jumpUrl, musicUrl, imageUrl):
        type_ = "Q0014"
        data_ = {"type": f"{type_}",
                 "data": {"wxid": f"{wxid}",
                          "name": f"{name}",
                          "author": f"{author}",
                          "app": "wx5aa333606550dfd5",
                          "jumpUrl": "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&tn=baidu&wd=%E4%BD%9C%E8%80%85%E6%B5%A9",
                          "musicUrl": f"{musicUrl}",
                          "imageUrl": "https://huyaimg.msstatic.com/avatar/1016/b9/b6824c9d5593f03f5b5c4f71189023_180_135.jpg?1564815405"},
                 }

        return self.post_(type_, data_)

    def api_get_qq_song_data(self, name):
        r = requests.get(f"http://114.116.54.227:9999/qqmusic/?name={name}", )

        return r.json()

    def send_qq_music_sharing(self, name, accept_wxid):
        r = requests.get(f"http://114.116.54.227:9999/qqmusic/?name={name}")
        jsondata = r.json()
        author = jsondata["author"]
        jumpUrl = jsondata["link"]
        musicUrl = jsondata["url"]
        imageUrl = jsondata["pic"]
        type_ = "Q0014"
        data_ = {"type": f"{type_}",
                 "data": {"wxid": f"{accept_wxid}",
                          "name": f"{name}",
                          "author": f"{author}",
                          "app": "wx5aa333606550dfd5",
                          "jumpUrl": f"{jumpUrl}",
                          "musicUrl": f"{musicUrl}",
                          "imageUrl": f"{imageUrl}"},
                 }

        return self.post_(type_, data_)

    def send_163_music_sharing(self, name, accept_wxid):
        r = requests.get(f"http://114.116.54.227:9999/163music/?name={name}")
        jsondata = r.json()
        author = jsondata["author"]
        jumpUrl = jsondata["link"]
        musicUrl = jsondata["url"]
        imageUrl = jsondata["pic"]
        type_ = "Q0014"
        data_ = {"type": f"{type_}",
                 "data": {"wxid": f"{accept_wxid}",
                          "name": f"{name}",
                          "author": f"{author}",
                          "app": "wx5aa333606550dfd5",
                          "jumpUrl": f"{jumpUrl}",
                          "musicUrl": f"{musicUrl}",
                          "imageUrl": f"{imageUrl}"},
                 }

        return self.post_(type_, data_)

# a = Robot(url="http://127.0.0.1:7777/DaenWxHook/httpapi/", wxid="wxid_at1vbqt6zgg922")
# bbb=a.get_friend_list()
# print(bbb)
# import information
# if __name__ == '__main__':
#     information.run()
#     print(1)
#     print(information.q.get())
