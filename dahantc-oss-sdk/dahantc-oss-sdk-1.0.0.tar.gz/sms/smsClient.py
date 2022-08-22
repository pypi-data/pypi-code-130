"""
  模块描述：短信模块服务调用
  @author 8522
  @date 2022-05-11 16:57:38
  版权所有 Copyright www.dahantc.com
"""
from common import util
from sms import smsConfig
import json
from sms import smsEntity


class SmsClient:
    # 服务调用一级地址，ip+端口或域名
    url = ""

    def __init__(self, url):
        self.url = url

    # 短信下发(相同内容多个号码)
    def sendSms(self, param):
        if type(param) != smsEntity.SmsSendParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数SmsSendParam")
        result = util.HttpUtil.doPost(self.url + smsConfig.SMS_SUBMIT, param.parseDict())
        return smsEntity.SmsSendResponse.parseObj(json.loads(result))

    # 短信下发(相同内容多个号码；签名在内容里)
    def sendSmsWithSign(self, param):
        if type(param) != smsEntity.SmsSendWSignParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数SmsSendWSignParam")
        result = util.HttpUtil.doPost(self.url + smsConfig.SMS_SUBMIT_WITH_SIGN, param.parseDict())
        return smsEntity.SmsSendWSignResponse.parseObj(json.loads(result))

    # 短信下发(不同内容多个号码)
    def sendSmsBatch(self, param):
        if type(param) != smsEntity.SmsSendBatchParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数SmsSendBatchParam")
        result = util.HttpUtil.doPost(self.url + smsConfig.SMS_SUBMIT_BATCH, param.parseDict())
        return smsEntity.BatchSendResponse.parseObj(json.loads(result))

    # 获取上行回复短信(接收手机回复的短信)
    def queryDeliver(self, param):
        if type(param) != smsEntity.DeliverParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数DeliverParam")
        result = util.HttpUtil.doPost(self.url + smsConfig.SMS_DELIVER, param.parseDict())
        return smsEntity.DeliverResponse.parseObj(json.loads(result))

    # 获取状态报告(确认手机接收情况)
    def queryReport(self, param):
        if type(param) != smsEntity.ReportParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数ReportParam")
        result = util.HttpUtil.doPost(self.url + smsConfig.SMS_REPORT, param.parseDict())
        return smsEntity.ReportResponse.parseObj(json.loads(result))

    # 查询余额(也包括彩信,语音,国际短信余额)
    def queryBalance(self, param):
        if type(param) != smsEntity.BalanceParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数BalanceParam")
        result = util.HttpUtil.doPost(self.url + smsConfig.SMS_BALANCE, param.parseDict())
        return smsEntity.BalanceResponse.parseObj(json.loads(result))