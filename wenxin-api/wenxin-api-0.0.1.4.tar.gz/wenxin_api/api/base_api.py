""" base api """
from typing import Optional
import wenxin_api
from wenxin_api import requestor, error
from wenxin_api.base_object import BaseObject
from wenxin_api.const import BASE_ERNIE_1P5B_MODEL_ID
from wenxin_api.error import IlleagalRequestArgumentError, InvalidResponseValue

class APIBaseObject(BaseObject):
    # hard code
    base_api_urls = ["http://dev020001.bcc-szth.baidu.com:8880/portal/api/rest/1.0/ernie/1.0/tuning",
                     "http://10.255.132.22:8080/task/deal_requests",
                     "http://dev020001.bcc-szth.baidu.com:8880/file/openApi/upload"]

    def __init__(self, 
                 ak=None, 
                 sk=None, 
                 api_type=0, 
                 base_model=BASE_ERNIE_1P5B_MODEL_ID,
                 **params):
        super(APIBaseObject, self).__init__(**params)
        self.__setattr__("ak", ak)
        self.__setattr__("sk", sk)
        self.__setattr__("api_type", api_type)
        self.__setattr__("base_model", base_model)

    @classmethod
    def default_request(
        cls,
        ak=None,
        sk=None,
        method="post",
        api_type=0,
        request_id=None,
        request_type=None,
        files=None,
        **params,
    ):
        try:
            api_type = int(api_type)
            url = cls.base_api_urls[api_type]
        except:
            raise IlleagalRequestArgumentError()
        if request_type is None:
            request_type = params.pop("type", None)

        http_requestor = requestor.HTTPRequestor(ak, sk, request_type)
        resp = http_requestor.request(url, method, files=files, request_id=request_id, **params)
        if not isinstance(resp, BaseObject) and isinstance(resp, list):
            InvalidResponseValue()
        return resp
    
    @classmethod
    def get_url(cls, api_type=0):
        try:
            api_type = int(api_type)
            url = cls.base_api_urls[api_type]
        except:
            raise IlleagalRequestArgumentError("api_type: {}".format(api_type))
        return url

class CreatableAPIObject(APIBaseObject):
    """ creatable api object """
    @classmethod
    def create(cls, ak=None, sk=None, api_type=0, request_id=None, **params):
        """ create """
        if isinstance(cls, APIBaseObject):
            raise ValueError(".create may only be called as a class method now.")
        request_type = params.pop("type", None)
        method = params.pop("method", "post")
        http_requestor = requestor.HTTPRequestor(ak, sk, request_type)
        url = cls.get_url(api_type)
        resp = http_requestor.request(url, method, request_id=request_id, **params)
        if not isinstance(resp, BaseObject):
            raise InvalidResponseValue("create method should returns BaseObject instance")
        return cls.construct_from(resp)

class DeletableAPIObject(APIBaseObject):
    """ deletable api object """
    @classmethod
    def delete(cls, ak=None, sk=None, api_type=0, request_id=None, **params):
        if isinstance(cls, APIBaseObject):
            raise ValueError(".delete may only be called as a class method now.")
        request_type = params.pop("type", None)
        method = params.pop("method", "post")
        http_requestor = requestor.HTTPRequestor(ak, sk, request_type)
        url = cls.get_url(api_type)
        resp = http_requestor.request(url, method, request_id=request_id, **params)
        if not isinstance(resp, BaseObject):
            raise InvalidResponseValue("delete method should returns BaseObject instance")
        return cls.construct_from(resp)

class StopableAPIObject(APIBaseObject):
    """ stopable api object """
    @classmethod
    def stop(cls, ak=None, sk=None, api_type=0, request_id=None, **params):
        request_type = params.pop("type", None)
        method = params.pop("method", "post")
        http_requestor = requestor.HTTPRequestor(ak, sk, request_type)
        url = cls.get_url(api_type)
        resp = http_requestor.request(url, method, request_id=request_id, **params)
        if not isinstance(resp, BaseObject):
            raise InvalidResponseValue("stop method should returns BaseObject instance")
        return cls.construct_from(resp)

class ListableAPIObject(APIBaseObject):
    """ listable api object """
    @classmethod
    def list(cls, ak=None, sk=None, api_type=0, request_id=None, **params):
        request_type = params.pop("type", None)
        method = params.pop("method", "post")
        if request_type is None:
            raise IlleagalRequestArgumentError("type is not provided")
        http_requestor = requestor.HTTPRequestor(ak, sk, request_type)
        url = cls.get_url(api_type)
        resps = http_requestor.request(url, method, request_id=request_id, **params)
        if isinstance(resps, BaseObject):
            return [cls.construct_from(resps)]
        resp = [cls.construct_from(r) for r in resps]
        return resp

class RetrievalableAPIObject(APIBaseObject):
    """ retrievalable api object """
    @classmethod
    def retrieve(cls, ak=None, sk=None, api_type=0, request_id=None, **params):
        if "type" not in params:
            raise IlleagalRequestArgumentError("type is not provided")
        request_type = params.pop("type", None)
        http_requestor = requestor.HTTPRequestor(ak, sk, request_type)
        method = params.pop("method", "post")
        url = cls.get_url(api_type)
        resp = http_requestor.request(url, method, request_id=request_id, **params)
        if not isinstance(resp, BaseObject):
            raise InvalidResponseValue("retrieve method should returns BaseObject instance")
        return cls.construct_from(resp)