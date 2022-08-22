"""
  模块描述：短信模板模块服务调用
  @author 8522
  @date 2022-05-11 10:57:38
  版权所有 Copyright www.dahantc.com
"""
import common.util as util
from sms import smsTempConfig
import json
from sms import smsTempEntity


class SmsTempClient:
    # 服务调用一级地址，ip+端口或域名
    url = ""

    def __init__(self, url):
        self.url = url

    # 短信模板上传
    def templateUpload(self, param):
        if type(param) != smsTempEntity.SmsTemplateUploadParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数SmsTemplateUploadParam")
        result = util.HttpUtil.doPost(self.url + smsTempConfig.TEMPLATE_UPLOAD, param.parseDict())
        return smsTempEntity.SmsTemplateUploadResponse.parseObj(json.loads(result))

    # 使用模板id下发
    def templateSubmit(self, param):
        if type(param) != smsTempEntity.SmsTemplateSubmitParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数SmsTemplateSubmitParam")
        result = util.HttpUtil.doPost(self.url + smsTempConfig.TEMPLATE_SUBMIT, param.parseDict())
        return smsTempEntity.SmsTemplateSubmitResponse.parseObj(json.loads(result))

    # 模板查询
    def templateShow(self, param):
        if type(param) != smsTempEntity.SmsTemplateShowParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数SmsTemplateShowParam")
        result = util.HttpUtil.doPost(self.url + smsTempConfig.TEMPLATE_SHOW, param.parseDict())
        return smsTempEntity.SmsTemplateShowResponse.parseObj(json.loads(result))

    # 模板删除
    def templateDelete(self, param):
        if type(param) != smsTempEntity.SmsTemplateDelParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数SmsTemplateDelParam")
        result = util.HttpUtil.doPost(self.url + smsTempConfig.TEMPLATE_DELETE, param.parseDict())
        return smsTempEntity.SmsTemplateDelResponse.parseObj(json.loads(result))