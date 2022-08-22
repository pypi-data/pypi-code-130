"""
  模块描述：工具类
  @author 8522
  @date 2022-05-11 13:00:38
  版权所有 Copyright www.dahantc.com
"""
import base64
import hashlib
import json
import requests


class FileUtil:
    """
        将本地某文件内容进行Base64加密
    """

    @staticmethod
    def getBase64Encode(path):
        f = open(path, mode="rb")
        data = f.read()
        f.close()
        return str(base64.b64encode(data))

    """
        获取本地某文件内容
    """

    @staticmethod
    def getBytes(path):
        f = open(path, mode="rb")
        data = f.read()
        f.close()
        return data


headers = {
    "Content-Type": "application/json"
}


# http工具类
class HttpUtil:
    # 发送post请求
    @staticmethod
    def doPost(url, param):
        postdata = json.dumps(param, ensure_ascii=False).encode('utf-8')
        res = requests.post(url, headers=headers, data=postdata)
        return res.content.decode("utf-8")


def md5Encode(context):
    hl = hashlib.md5()
    hl.update(context.encode(encoding='utf8'))
    return hl.hexdigest()


# entity工具类
class EntityUtil:
    # 获取字典的某属性值，当不存在该key时返回空
    @staticmethod
    def getValue(val, key):
        if type(val) != dict:
            raise Exception("val参数必须为字典类型")
        return val[key] if key in val.keys() else ""
