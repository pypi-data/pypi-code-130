import requests
import json
from uts import utils

def post(url,endpoint,host,payload,token):

    headers = {
        "Host" : host,
        "Content-Type" : 'application/json',
        "Authorization" : 'Bearer ' + token
    }

    request = requests.post(url+endpoint,data=json.dumps(payload),headers=headers)

    if(utils.validate(request,endpoint)):
        return request.text

def get(url,endpoint,host,payload,token):

    headers = {
        "Host" : host,
        "Content-Type" : 'application/json',
        "Authorization" : 'Bearer ' + token
    }

    request = requests.get(url+endpoint+payload,{},headers=headers)

    if(utils.validate(request,endpoint)):
        return request.text