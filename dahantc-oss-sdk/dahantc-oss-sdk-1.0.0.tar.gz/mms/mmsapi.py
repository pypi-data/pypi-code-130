"""
  模块描述：彩信发送client
  @author 8526
  @date 2022-05-12 11:00:38
  版权所有 Copyright www.dahantc.com
"""
import json

import dicttoxml
import requests
import xmltodict

import mms.conf as conf
import mms.param as param
import mms.response as res


# 彩信调用工具
class MmsClient:

    def __init__(self, base_url):
        if base_url is None:
            base_url = conf.BASE_URL
        self.base_url = base_url

    # 彩信发送
    def mmsSend(self, params):
        if type(params) != param.MmsSendParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数MmsSendParam")
        bxml = dicttoxml.dicttcxml(params.parseDict(), custom_root='root')
        xmlStr = bxml.decode('utf-8')
        result = requests.get(self.base_url + conf.MMS_URL, params=xmlStr)
        data = xmltodict.parse(result.content)
        jsonStr = json.loads(json.dumps(data))
        return res.mmsSendResponseDecoder(jsonStr)

    # 查询彩信报告
    def queryReport(self, params):
        if type(params) != param.MmsReportParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数MmsReportParam")
        bxml = dicttoxml.dicttoxml(params.parseDict(), custom_root='root')
        xmlStr = bxml.decode('utf-8')
        result = requests.get(self.base_url + conf.MMS_URL, params=xmlStr)
        data = xmltodict.parse(result.content)
        jsonStr = json.loads(json.dumps(data))
        return res.mmsReportResponseDecoder(jsonStr)


if __name__ == '__main__':
    head = param.MmsHead('002', 'ac', 'pwd')
    params = param.MmsReportParam(head)
    client = MmsClient(None)
    print(client.queryReport(params).__dict__)
    submitmsg = param.SubmitMsg('phone', 'title', 'content', 'msgid', 'subcode')
    sendparam = param.MmsSendParam(head, param.MmsSendBody([submitmsg]))
    res = client.mmsSend(sendparam)
    print(res)
