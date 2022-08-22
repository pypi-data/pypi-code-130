"""
  模块描述：
  @author 8526
  @date 2022-05-13 9:06:41
  版权所有 Copyright www.dahantc.com
"""
from distutils.core import setup

setup(
    name='dahantc-oss-sdk',
    version='1.0.0',
    author='8526',
    description='大汉三通平台模块',
    long_description='oss 平台业务功能调用',
    url='https://gitee.com/dahanoss/sdk-python',
    packages=['common', 'errorphone', 'mms', 'shorturl', 'sms', 'smsstatistics', 'supermsg', 'voice']
)
