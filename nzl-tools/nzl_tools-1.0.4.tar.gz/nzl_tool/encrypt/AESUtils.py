#!D:/Code/python
# -*- coding: utf-8 -*-
# @Time :2020/12/16 10:45
# @Author : NZL
# @File : AESUtils.py
# @Desc : AES加密工具   导包  pycryptodome==3.12.0
import Crypto.Cipher.AES
import json
import base64
import logging
import warnings

warnings.simplefilter("ignore")

KEY = 'AESUtils2022'


class AesEncrypt(object):

    def __init__(self, key):
        self.key = key
        if len(self.key) < 16:
            self.key = '%s0000000000000000' % self.key
        self.key = str(self.key[0:16]).encode("utf-8")

    def encrypt(self, data):
        data = json.dumps(data).replace('"', '')
        mode = Crypto.Cipher.AES.MODE_ECB
        padding = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
        crypts = Crypto.Cipher.AES.new(self.key, mode)
        cipher_text = crypts.encrypt(padding(data).encode("utf-8"))
        return base64.b64encode(cipher_text).decode("utf-8")

    def decrypt(self, data):
        crypts = Crypto.Cipher.AES.new(self.key, Crypto.Cipher.AES.MODE_ECB)
        decryptBytes = base64.b64decode(data)
        meg = crypts.decrypt(decryptBytes).decode('utf-8')
        return meg[:-ord(meg[-1])]


def aes_decrypt(ciphertext, key=KEY):
    """
    解密
    :param ciphertext: 密文内容
    :param key: 解密所用的密钥，不设置则使用默认
    :return:
    """
    try:
        aes = AesEncrypt(key)
        res = str(aes.decrypt(ciphertext))
        res_len = len(res)
        frond_char = res[0:1]
        end_char = res[res_len - 1:res_len]
        if end_char == '"':
            res = res[0: res_len - 1]
        if frond_char == '"':
            res = res[1: len(res)]
        return str(res.encode('utf8').decode('unicode_escape'))
    except Exception as e:
        logging.error('AES加密出错：%s' % e)
        return None


def aes_encrypt(content, key=KEY):
    """
    加密
    :param content:  需要加密的内容
    :param key: 加密所用的密钥，不设置则使用默认
    :return:
    """
    try:
        aes = AesEncrypt(key)
        return aes.encrypt(content)
    except Exception as e:
        logging.error('AES解密出错：%s' % e)
        return None

