from uts import utils
import requests
import json

class Authentication(object):
    token = ''

    def __init__(self):
        pass

    def login(self,apiKey,host,url):
        endpoint = '/public/api/login'
        headers = {
                "Host" : host,
                "Content-Type" : 'application/json',
        }
        payload = {
            "apikey" : apiKey
        }
        request = requests.post(url+endpoint,data=json.dumps(payload),headers=headers)
        if(utils.validate(request,endpoint)):
            self.token = json.loads(request.text)["access_token"]
        else:
            print(json.loads(request.text))