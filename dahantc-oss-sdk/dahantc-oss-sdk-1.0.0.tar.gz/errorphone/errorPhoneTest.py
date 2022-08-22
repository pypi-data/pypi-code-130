import unittest
from errorphone import errorPhoneEntity
from errorphone.errrorPhoneClient import ErrorPhoneClient

account = "dhst8526"
password = "bb43a2c4081bec02fca7b72f38e63021"
client = ErrorPhoneClient("http://180.168.192.126:13866")


class MyTestCase(unittest.TestCase):
    # 号码状态查询
    def test_qryPhoneStatus(self):
        param = errorPhoneEntity.QryPhoneStatusParam(account, password, "18552440714,185****0716")
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.qryPhoneStatus(param).parseDict()))

    # 号码属性查询
    def test_qryPhoneProperty(self):
        param = errorPhoneEntity.QryPhonePropertyParam(account, password, "18552440714,185****0716")
        print("入参：" + str(param.parseDict()))
        print("返参：" + str(client.qryPhoneProperty(param).parseDict()))


if __name__ == '__main__':
    unittest.main()
