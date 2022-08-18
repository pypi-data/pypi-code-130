import requests
import hashlib
import os
import time

__remote_global__ = {}

def SET_URL(url):
    """
    设置转发服务器地址, 一次设置, 永久生效
    """
    with open(os.path.join(os.path.dirname(__file__), "url_temp"), "w", encoding="utf-8") as fp:
        fp.write(url)

def SHOW_URL():
    with open(os.path.join(os.path.dirname(__file__), "url_temp"), "r", encoding="utf-8") as fp:
        print(fp.read())

def print_remote(user_ids:list, server_name:str, message:str, party_ids:list=[]):
    user_id = "|".join(user_ids)
    party_id = "|".join(party_ids)
    try:
        with open(os.path.join(os.path.dirname(__file__), "url_temp"), "r", encoding="utf-8") as fp:
            url = fp.read()
    except:
        print("无法读取有效url, 请重新设置(SET_URL)")
    try:
        re = requests.get(url + f"?userId={user_id}&partyId={party_id}&serverName={server_name}&message={message}")
        if re.status_code != 200:
            print("远程消息递送失败!")
    except Exception as e:
            print(f"远程消息递送失败! {str(e)}")

def print_remote_once(user_ids:list, server_name:str, message:str, party_ids:list=[], time_range=7200):
    """
    一定时间内不重复发消息
    """
    user_id = "|".join(user_ids)
    party_id = "|".join(party_ids)
    hash_value = hashlib.md5()
    hash_value.update((user_id + server_name + message + party_id).encode("utf-8"))
    hash_value = hash_value.hexdigest()
    if __remote_global__.get(hash_value, None) != None:
        now_time = time.time()
        if now_time < __remote_global__[hash_value] + time_range:
            return
        else:
            __remote_global__[hash_value] = now_time
    else:
        __remote_global__[hash_value] = time.time()

    try:
        with open(os.path.join(os.path.dirname(__file__), "url_temp"), "r", encoding="utf-8") as fp:
            url = fp.read()
    except:
        print("无法读取有效url, 请重新设置(SET_URL)")
    try:
        re = requests.get(url + f"?userId={user_id}&partyId={party_id}&serverName={server_name}&message={message}")
        if re.status_code != 200:
            print("远程消息递送失败!")
    except Exception as e:
            print(f"远程消息递送失败! {str(e)}")