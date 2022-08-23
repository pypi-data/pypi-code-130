import requests
import hashlib
import traceback
import json

class HttpClient(object):
    def __init__(self):
        self.session = requests.Session()

    def request(self,requestMethod,requesturl,paramMethod = None,requestData = None,headers = None,**kwargs):
        try:
            if requestMethod.lower() == "post":
                return self.__post(requesturl,paramMethod,requestData=requestData,headers=headers,**kwargs)
            elif requestMethod.lower() == "get":
                return self.__get(requesturl,requestData = requestData,headers=headers,**kwargs)
            elif requestMethod.lower() == "patch":
                return self.__patch(requesturl,paramMethod,requestData=requestData,headers=headers,**kwargs)
            elif requestMethod.lower() == "delete":
                return self.__delete(requesturl, paramMethod, requestData=requestData, headers=headers, **kwargs)
        except Exception as e:
            print(traceback.format_exc())


    def __post(self,requesturl,paramMethod,requestData = None,headers = None,**kwargs):
        try:
            if paramMethod == "form" or paramMethod == "data":
                responseObj =self.session.post(url=requesturl,data=requestData,headers=headers,**kwargs)
                return responseObj
            elif paramMethod == 'json':
                responseObj =self.session.post(url=requesturl, json=requestData, headers=headers, **kwargs)
                return responseObj
        except Exception as e:
            print(traceback.format_exc())

    def __get(self,requestUrl,requestData = None,headers=None,**kwargs):

        try:
            if requestData:
                responseObj = self.session.get(url=requestUrl,data=requestData,headers=headers,**kwargs)
                return responseObj
            else:
                # print('11111',requestUrl)
                responseObj = self.session.get(url=requestUrl,headers=headers,**kwargs)
                return responseObj
        except Exception as e:
            print(traceback.format_exc())

    def __delete(self,requesturl,paramMethod,requestData = None,headers = None,**kwargs):
        try:
            if paramMethod == "form" or paramMethod == "data":
                responseObj =self.session.delete(url=requesturl,data=requestData,headers=headers,**kwargs)
                return responseObj
            elif paramMethod == 'json':
                responseObj =self.session.delete(url=requesturl, json=requestData, headers=headers, **kwargs)
                return responseObj
        except Exception as e:
            print(traceback.format_exc())

    def __patch(self,requesturl,paramMethod,requestData = None,headers = None,**kwargs):
        try:
            if paramMethod == "json" or paramMethod == "data":
                responseObj =self.session.patch(url=requesturl,data=requestData,**kwargs)
                return responseObj
        except Exception as e:
            print(traceback.format_exc())



if __name__ == '__main__':
    hh = HttpClient()
    res = hh.request("get", "https://preview.iotdataserver.net/api/auth/certification/captcha2")
    print(res.json())
    assert res.json()['code'] == 200
    # print(json.dumps(res.json(), sort_keys=True, indent=4, ensure_ascii=False))
