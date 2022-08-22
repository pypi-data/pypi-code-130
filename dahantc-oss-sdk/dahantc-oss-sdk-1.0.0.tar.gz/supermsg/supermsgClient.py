"""
  模块描述：超级短信模块服务调用
  @author 8522
  @date 2022-05-11 16:39:38
  版权所有 Copyright www.dahantc.com
"""

from common import util
from supermsg import supermsgConfig
import json
from supermsg import supermsgEntity


class SupermsgClient:
    # 服务调用一级地址，ip+端口或域名
    url = ""

    def __init__(self, url):
        self.url = url

    # 上传超级短信模板
    def upTemp(self, param):
        if type(param) != supermsgEntity.UpSupermsgTempParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数UpSupermsgTempParam")
        param.cmdId = "001"
        result = util.HttpUtil.doPost(self.url + supermsgConfig.path, param.parseDict())
        return supermsgEntity.UpSupermsgTempResponse.parseObj(json.loads(result))

    # 超级短信审核状态查询
    def qryExamine(self, param):
        if type(param) != supermsgEntity.ExamineReportParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数ExamineReportParam")
        param.cmdId = "003"
        result = util.HttpUtil.doPost(self.url + supermsgConfig.path, param.parseDict())
        return supermsgEntity.ExamineReportResponse.parseObj(json.loads(result))

    # 超级短信下发
    def sendSupermsg(self, param):
        if type(param) != supermsgEntity.SendSupermsgParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数SendSupermsgParam")
        param.cmdId = "002"
        result = util.HttpUtil.doPost(self.url + supermsgConfig.path, param.parseDict())
        return supermsgEntity.SendSupermsgResponse.parseObj(json.loads(result))

    # 获取超级短信状态报告
    def qrySendReport(self, param):
        if type(param) != supermsgEntity.QrySendReportParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数QrySendReportParam")
        param.cmdId = "004"
        result = util.HttpUtil.doPost(self.url + supermsgConfig.path, param.parseDict())
        return supermsgEntity.QrySendReportResponse.parseObj(json.loads(result))