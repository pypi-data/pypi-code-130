# from tkinter import NW
import requests
import hashlib
import time
from urllib import parse
import json

now = time.localtime()
now_time = time.strftime("%Y%m%d%H%M%S", now)
# print(now_time)
m = hashlib.md5()
username = "Customer"
password = "abccus123"
token = username+password+now_time
m.update(token.encode())
md5 = m.hexdigest()
# print(md5)

# data = {
#     "operationinfo": {
#         "operator": "24"
#     },
#     "mainTable": {
#         "id": ""
#     },
#     "pageInfo": {
#         "pageNo": "1",
#         "pageSize": "100"
#     },
#     "header": {
#         "systemid": username,
#         "currentDateTime": now_time,
#         "Md5": md5
#     }
# }

data = {
			"operationinfo":{
				"operator":"DMS"
			},
			"mainTable":{},
			"pageInfo":{
				"pageNo":"1",
				"pageSize":"10000"
			},
			"header": {
				"systemid": "Customer",
				"currentDateTime": now_time,
				"Md5": md5
			}
		}

str = json.dumps(data, indent=2)
# print(str)
values = parse.quote(str).replace("%20", "")
# print(values)
url = "http://192.168.1.15:32212/api/cube/restful/interface/getModeDataPageList/CustomerList"

payload = 'datajson='+values
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}
response = requests.request("POST", url, headers=headers, data=payload)

info = response.json()['result']

print(info)
