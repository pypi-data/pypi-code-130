"""
  模块描述：异常号码检测模块服务调用
  @author 8522
  @date 2022-05-11 15:33:38
  版权所有 Copyright www.dahantc.com
"""
from common import util
from errorphone import errorPhoneConfig
import json
from errorphone import errorPhoneEntity


class ErrorPhoneClient:
    # 服务调用一级地址，ip+端口或域名
    url = ""

    def __init__(self, url):
        self.url = url

    # 号码状态查询
    def qryPhoneStatus(self, param):
        if type(param) != errorPhoneEntity.QryPhoneStatusParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数QryPhoneStatusParam")
        result = util.HttpUtil.doPost(self.url + errorPhoneConfig.phoneStatusPath, param.parseDict())
        return errorPhoneEntity.QryPhoneStatusResponse.parseObj(json.loads(result))

    # 号码属性查询
    def qryPhoneProperty(self, param):
        if type(param) != errorPhoneEntity.QryPhonePropertyParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数QryPhonePropertyParam")
        result = util.HttpUtil.doPost(self.url + errorPhoneConfig.phonePropertyPath, param.parseDict())
        return errorPhoneEntity.QryPhonePropertyResponse.parseObj(json.loads(result))