#!D:/Code/python
# -*- coding: utf-8 -*-
# @Time :2021/3/20 13:48
# @Author : NZL
# @File : DesUtils.py
# @Desc : Des加密解密  导包  pyDes==2.0.1
import logging
import warnings
from nzl_tool.encrypt import pyDes

DES_KEY = 'DesUtils2022'

warnings.simplefilter("ignore")


def des_encrypt(secret_str, des_key_=DES_KEY):
    """
    加密
    :param secret_str: 密文字符串
    :param des_key_: 加密所用的密钥，不设置则使用默认
    :return:
    """
    res = ''
    try:
        des_key = '%s00000000' % str(des_key_)
        des_key = str(des_key)[0:8]
        des_obj = pyDes.des(des_key, pyDes.ECB, des_key, padmode=pyDes.PAD_PKCS5)
        s = secret_str.encode('utf-8')
        secret_bytes = des_obj.encrypt(s)  # 用对象的encrypt方法加密
        res = secret_bytes.hex()
    except Exception as e:
        logging.error("des解密失败，密文：%s ,密钥：%s, e:%s" % (secret_str, des_key_, e))
    return None if res == '' else res


def des_decrypt(secret_str, des_key_=DES_KEY):
    """
    解密
    :param secret_str: 密文
    :param des_key_:解密所用的密钥，不设置则使用默认
    :return:
    """
    res = ''
    try:
        des_key = '%s00000000' % str(des_key_)
        des_key = str(des_key)[0:8]
        des_obj = pyDes.des(des_key, pyDes.ECB, des_key, padmode=pyDes.PAD_PKCS5)
        secret_bytes = bytes.fromhex(secret_str)
        s = des_obj.decrypt(secret_bytes)
        res = s.decode()
    except Exception as e:
        logging.error("des解密失败，密文：%s ,密钥：%s, e:%s" % (secret_str, des_key_, e))
    return None if res == '' else res

