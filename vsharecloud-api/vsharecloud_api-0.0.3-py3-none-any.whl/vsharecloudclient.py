import os
import sys
import requests
import base64
import rsa
import json
from typing import Union, List, Dict, Tuple

class Client:
    url_host = "https://api.vshare.cloud"
    def __init__(self,private_key:bytes,user_id:int):
        """"""
        self.private_key = private_key
        self.PrivateKey = rsa.PrivateKey.load_pkcs1(private_key)
        self.user_id = user_id
        self.balance = None
        
    def _makerequest(self,url:str,data:dict)->dict:
        data["uid"] = self.user_id
        sdata = json.dumps(data)
        sign = rsa.sign(sdata.encode(), self.PrivateKey, 'SHA-256')
        rdata = {
            "data": str(base64.b64encode(sdata.encode()), 'utf-8'),
            "sign": str(base64.b64encode(sign), 'utf-8')
        }
        r = requests.post(url, data=rdata)
        if r.status_code != 200:
            raise Exception("Request failed with status code {}, content is {}".format(r.status_code, r.content))
        return r.json()

    def getuserinfo(self):
        """"""
        url = self.url_host + "/api/v1/userinfo"
        ret = self._makerequest( url,{})
        if ret["status"] != True:
            raise Exception(json.dumps(ret))
        self.balance = ret["data"]["money"]
        return ret["data"]

    def getfilelist(self):
        """"""
        url = self.url_host + "/api/v1/filelist"
        ret = self._makerequest( url,{})
        if ret["status"] != True:
            raise Exception(json.dumps(ret))
        return ret["data"]

    def getfileinfo(self,cid:str):
        """"""
        url = self.url_host + "/api/v1/getfile"
        ret = self._makerequest( url,{"cid":cid})
        if ret["status"] != True:
            raise Exception(json.dumps(ret))
        return ret["data"]
    
    def addfile(self,cid:str,filename:Union[str,None]=None):
        """"""
        url = self.url_host + "/api/v1/addfile"
        data = {"cid":cid}
        if filename:
            data["filename"] = filename
        ret = self._makerequest( url,data)
        if ret["status"] != True:
            raise Exception(json.dumps(ret))
        return True

    def delfile(self,cid:str):
        """"""
        url = self.url_host + "/api/v1/delfile"
        ret = self._makerequest( url,{"cid":cid})
        if ret["status"] != True:
            raise Exception(json.dumps(ret))
        return True

    @staticmethod
    def genkeys():
        (pubkey, privkey) = rsa.newkeys(2048)
        return pubkey, privkey

