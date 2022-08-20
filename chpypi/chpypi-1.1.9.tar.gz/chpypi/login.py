import requests
import logging








class LOGIN:
    def __init__(self):
        ...

    def zhogntai(self,username,password):
        for _ in range(3):
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
                }
                data = {
                    "username": username,
                    "password": password
                }
                rsp = requests.post(url='https://console.itaxs.com/api/admin/login/token', headers=headers, data=data, verify=False,timeout=20)
                jData = rsp.json()
                message = jData.get('message')
                if message == "success":
                    logging.info('----------------  登录成功，返回token  ----------------')
                    token = jData.get("data").get("access_token")
                    return token
            except Exception as e:
                logging.info('----------------  登录失败  ----------------')