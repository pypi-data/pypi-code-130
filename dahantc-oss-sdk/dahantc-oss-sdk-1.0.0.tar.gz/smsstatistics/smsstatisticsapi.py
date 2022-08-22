"""
  模块描述：统计api 模块
  @author 8526
  @date 2022-05-12 10:53:05
  版权所有 Copyright www.dahantc.com
"""
import json

import requests

import common.util as util
import smsstatistics.conf as conf
import smsstatistics.param as param
import smsstatistics.response as res


# 短信统计client
class SmsStatisticsClient:
    def __init__(self, base_url):
        # 可配置的调用前缀
        if base_url is None:
            base_url = conf.BASE_URL
        self.base_url = base_url

    # 短信统计方法
    def sms_statistics(self, params):
        if type(params) != param.SmsStatisticsParam:
            raise Exception("参数类型有误，请使用SDK提供的class参数SmsStatisticsParam")
        param_json = json.dumps(params.parseDict())
        result = requests.post(self.base_url + conf.SMS_STATISTICS_REPORT, headers={'content-type': 'application/json'},
                               data=param_json)
        return res.smsStatisticsResponseDecoder(json.loads(result.content))


if __name__ == '__main__':
    pwdMd5 = util.md5Encode("456.com")
    account = "dhst8526"
    client = SmsStatisticsClient('http://180.168.192.126:16766')
    smsparam = param.SmsStatisticsParam(account, pwdMd5, '20220101', '20220501', 1, 0)
    res = client.sms_statistics(smsparam)
    print(res.__dict__)
