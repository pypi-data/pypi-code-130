"""
  模块描述：接口响应
  @author 8526
  @date 2022-05-12 10:15:33
  版权所有 Copyright www.dahantc.com
"""


# 短信统计响应
class SmsStatisticsResponse:
    def __init__(self, result, desc, data):
        # 该次请求提交结果
        self.result = result
        # 描述
        self.desc = desc
        # 统计结果
        self.data = data


# 响应详细数据
class SmsStatisticDataRes:
    def __init__(self, submitFailCount, sendFailCount, sendTotalCount, statsDate, successCount, successRatio):
        # 提交失败数
        self.submitFailCount = submitFailCount
        # 发送失败数
        self.sendFailCount = sendFailCount
        # 发送总数
        self.sendTotalCount = sendTotalCount
        # 统计时间
        self.statsDate = statsDate
        # 发送成功数
        self.successCount = successCount
        # 成功率 = 成功数/总数
        self.successRatio = successRatio


def smsStatisticsResponseDecoder(obj):
    if obj is None:
        return None
    return SmsStatisticsResponse(obj.get('result'), obj.get('desc'), smsStatisticsDataDecoder(obj.get('data')))


def smsStatisticsDataDecoder(obj):
    if obj is None:
        return None
    data = []
    for val in obj:
        data.append(
            SmsStatisticDataRes(val.get('submitFailCount'), val.get('sendFailCount'), val.get('sendTotalCount'),
                                val.get('statsDate'), val.get('successCount'), val.get('successRatio')))
    return data
