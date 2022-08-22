import unittest
from sms import smsEntity
from sms.smsClient import SmsClient

# 短信模块服务调用对象
account = "dhst8526"
password = "bb43a2c4081bec02fca7b72f38e63021"
client = SmsClient("http://180.168.192.126:16766")


class MyTestCase(unittest.TestCase):

    # 短信下发(相同内容多个号码)-测试
    def test_sendSms(self):
        param = smsEntity.SmsSendParam(account, password, "2c92825934837c4d0134837dcba00150", "15711665563,15711651145",
                                       "您好，您的手机验证码为：430237。", "【大汉三通】", "", "", "", "", "")
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.sendSms(param).parseDict()))

    # 短信下发(相同内容多个号码；签名在内容里)
    def test_sendSmsWithSign(self):
        param = smsEntity.SmsSendWSignParam(account, password, "2c92825934837c4d0134837dcba00150",
                                            "1571163378,15711655522", "【大汉三通】您好，您的手机验证码为：430237。", "", "20220516180000",
                                            {"1": "A", "2": "B"}, "", "")
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.sendSmsWithSign(param).parseDict()))

    # 短信下发(不同内容多个号码)
    def test_sendSmsBatch(self):
        data = []
        b1 = smsEntity.BaseSendData("93786e387cf6462b9b60a36f8e7f1b27", "11111111,1571166****,173878****",
                                    "您好！你有一个快递,请注意查收。", "【客户签名】", "", "", {"1": "A", "2": "B"}, "", "")
        b2 = smsEntity.BaseSendData("93786e387cf6462b9b60a36f8e7f1b28", "1571166****,17387815244",
                                    "您好！你有一个快递,请注意查收。", "【客户签名】", "", "", {"1": "A", "2": "B"}, "", "")
        data.append(b1)
        data.append(b2)
        param = smsEntity.SmsSendBatchParam(account, password, data)
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.sendSmsBatch(param).parseDict()))

    # 获取上行回复短信(接收手机回复的短信)
    def test_queryDeliver(self):
        param = smsEntity.DeliverParam(account, password)
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.queryDeliver(param).parseDict()))

    # 获取状态报告(确认手机接收情况)
    def test_queryReport(self):
        param = smsEntity.ReportParam(account, password)
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.queryReport(param)))

    # 查询余额(也包括彩信,语音,国际短信余额)
    def test_queryBalance(self):
        param = smsEntity.BalanceParam(account, password)
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.queryBalance(param).parseDict()))


if __name__ == '__main__':
    unittest.main()
