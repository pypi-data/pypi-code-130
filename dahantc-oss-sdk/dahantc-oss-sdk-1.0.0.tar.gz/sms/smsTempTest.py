import unittest
from sms import smsTempEntity
from sms.smsTempClient import SmsTempClient

# 短信模块服务调用对象
account = "dhst8526"
password = "bb43a2c4081bec02fca7b72f38e63021"
client = SmsTempClient("http://180.168.192.126:16766")


class MyTestCase(unittest.TestCase):

    # 短信模板上传
    def test_templateUpload(self):
        param = smsTempEntity.SmsTemplateUploadParam(account, password, "【大汉三通】", "你好，这是白模板${1,10}示例", "")
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.templateUpload(param).parseDict()))

    # 使用模板id下发
    def test_templateSubmit(self):
        variables = []
        variables.append(smsTempEntity.SmsTemplateVariable("1", "内容1"))
        variables.append(smsTempEntity.SmsTemplateVariable("2", "内容2"))
        template = smsTempEntity.SmsTemplateData("2c9289788092247f0180d0c15c920008", variables)
        param = smsTempEntity.SmsTemplateSubmitParam(account, password, "15200223574", template,
                                                     "2c92825934837c4d0134837dcba00150", "", "",
                                                     {"param1": "aaa", "param2": "bbb"}, "")
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.templateSubmit(param).parseDict()))

    # 模板查询
    def test_templateShow(self):
        param = smsTempEntity.SmsTemplateShowParam(account, password,
                                                   "2c9289788092247f0180b70739380006,2c9289788092247f0180d0c15c920008")
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.templateShow(param).parseDict()))

    # 模板删除
    def test_templateDelete(self):
        param = smsTempEntity.SmsTemplateDelParam(account, password,
                                                  "2c9289788092247f0180b70739380002,2c9289788092247f0180d0c15c920004")
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.templateDelete(param).parseDict()))


if __name__ == '__main__':
    unittest.main()
