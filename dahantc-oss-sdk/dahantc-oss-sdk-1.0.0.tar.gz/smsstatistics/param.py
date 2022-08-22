"""
  模块描述：shorturl接口参数
  @author 8526
  @date 2022-05-12 10:15:33
  版权所有 Copyright www.dahantc.com
"""

import common.entity as entity


class BaseJsonable(object):

    def parseDict(self):
        d = {}
        d.update(self.__dict__)
        return d


# 短信统计入参
class SmsStatisticsParam(entity.BaseParam, BaseJsonable):
    def __init__(self, account, password, starttime, endtime, messagetype, tjtype):
        super().__init__(account, password)
        # 统计开始日期，距统计结束日期最多3个月，格式为yyyyMMdd,必填
        self.starttime = starttime
        # 统计结束日期，允许的最大值为当前日期往前推三天。格式为yyyyMMdd,必填
        self.endtime = endtime
        # 查询类别，1表示短信统计查询，默认值为1
        self.messagetype = messagetype
        # 取值0或1,0表示获取统计总数，1表示获取按天统计结果。（当 type取值为0时，为统计总数，返回的统计日期字段值为空）
        self.tjtype = tjtype
