import json
import base64
import time
import requests
import threading
import base64
import heroku3
from uuid import UUID
from os import urandom
from time import timezone, sleep
from typing import BinaryIO, Union
from binascii import hexlify
from time import time as timestamp
from locale import getdefaultlocale as locale
from json_minify import json_minify
from .lib.util import deviceId
from .lib.util import headers, helpers, device

#@dorthegra/IDörthe#8835 thanks for support!
device = device.DeviceGenerator()

class Client():
    def __init__(self,app_name:str=None,key:str=None, deviceId: str = None):
        self.api = "https://service.narvii.com/api/v1"
        self.heroku=f"https://{app_name}.herokuapp.com"
        self.key=key
        self.app_name=app_name
        if deviceId: self.device_id = deviceId
        else: self.device_id = device.device_id
        self.user_agent = device.user_agent
        self.sid = None
        self.userId = None
        
    def res(self):
        heroku_conn = heroku3.from_key(self.key)
        botapp= heroku_conn.apps()[self.app_name]
        botapp.restart()       

    def login_sid(self, SID: str):
        """
        Login into an account with an SID
        **Parameters**
            - **SID** : SID of the account
        """
        uId = helpers.sid_to_uid(SID)
        self.authenticated = True
        self.sid = SID
        self.userId = uId

        headers.sid = self.sid
        headers.userId = self.userId

    def parse_headers(self, data: str = None, type: str = None):
        return headers.ApisHeaders(deviceId=deviceId(), data=data, type=type).headers

	
    def sendActive(self,comId: str,tz: int = -time.timezone // 1000):
	    
	        """
	        Send A Active Time To Community
	        **Returns**
	           
	        """
	        data = {"timestamp": int(time.time() * 1000), "optInAdsFlags": 2147483647, "timezone": tz}
	        timers=[{'start': int(time.time()), 'end': int(time.time()) + 300} for _ in range(25)]
	        data["userActiveTimeChunkList"] = timers
	        dat = json_minify(json.dumps(data))
	        response = requests.post(f"https://service.narvii.com/api/v1/x{comId}/s/community/stats/user-active-time", headers=self.parse_headers(dat), data=dat)
	        if response.status_code == 403:
	        	error=json.dumps({"api:statuscode":69,"api:message":"wait ip is changing"})
	        	self.res()
	        	return error
	        else:
	            resp=response.json()
	            if resp["api:statuscode"]==110:
	                self.res()
	                return resp
	            return resp


    def coin_gen(self,sid:str, comId: int):
        
        data = json.dumps({})
        response = requests.post(f"{self.heroku}/{comId}/send-active-obj/{sid}", data = data)
        try:
            if response.json()["api:statuscode"]==69 or response.json()["api:statuscode"]==110:
                print(response.json()["api:message"])
                time.sleep(7)
                res=requests.post(f"{self.heroku}/{comId}/send-active-obj/{sid}", data = data)
                print(res.text)
                return res
            else:
                print(response.text)
                return response.json()
        except:
            pass