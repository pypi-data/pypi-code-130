import unittest
from supermsg import supermsgEntity
from supermsg.supermsgClient import SupermsgClient

account = "dhst8526"
password = "bb43a2c4081bec02fca7b72f38e63021"
client = SupermsgClient("http://180.168.192.126:13766")


class MyTestCase(unittest.TestCase):
    # 上传超级短信模板
    def test_upTemp(self):
        content = []
        temp1 = supermsgEntity.SupermsgTemp("img.jpg", "文件64位编码", "1_1")
        temp2 = supermsgEntity.SupermsgTemp("", "${2,20}是一座美丽的城市，我爱${2,20}！", "1_2")
        temp3 = supermsgEntity.SupermsgTemp("", "${2,10}特产有：${1,10}、${1,10}、${1,10}等。", "1_3")
        content.append(temp1)
        content.append(temp2)
        content.append(temp3)
        param = supermsgEntity.UpSupermsgTempParam(account, password, "标题", content)
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.upTemp(param).parseDict()))

    # 超级短信审核状态查询
    def test_qryExamine(self):
        param = supermsgEntity.ExamineReportParam(account, password, "ff808081804659220180b79a1bfb0013")
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.qryExamine(param).parseDict()))

    # 超级短信下发
    def test_sendSupermsg(self):
        param = supermsgEntity.SendSupermsgParam(account, password, "2c9282396ab3dbbe016ab3f7984b001",
                                                 "130520369**,130520369**,13052036911", "3333",
                                                 "上海#####上海#####上海#####上海木雕#####城隍庙五香豆#####嘉定竹刻")
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.sendSupermsg(param).parseDict()))

    # 获取超级短信状态报告
    def test_qrySendReport(self):
        param = supermsgEntity.QrySendReportParam(account, password)
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.qrySendReport(param).parseDict()))


if __name__ == '__main__':
    unittest.main()
