"""
  模块描述：公共实体类
  @author 8522
  @date 2022-05-11 11:00:38
  版权所有 Copyright www.dahantc.com
"""


# 入参基础参数
class BaseParam:
    # 用户账号
    account = ""
    # 账号密码，需采用MD5加密(32位小写)
    password = ""

    def __init__(self, account, password):
        self.account = account
        self.password = password


# 返参基础参数
class BaseResult:
    # 返回状态码，必返
    result = ""
    # 描述，必返
    desc = ""
    # TODO
    # 错误描述
    msg = ""

    def __init__(self, result, desc, msg):
        self.result = result
        self.desc = desc
        self.msg = msg
