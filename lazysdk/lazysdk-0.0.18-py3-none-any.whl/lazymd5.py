#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
import hashlib


def md5_file(
        file_path
):
    # 文件名不影响md5
    d5 = hashlib.md5()
    with open(r'%s' % file_path, 'rb') as f:
        while True:
            data = f.read(2048)
            if not data:
                break
            d5.update(data)  # update添加时会进行计算
    return d5.hexdigest()


def md5_str(
        content,
        encoding='UTF-8'
):
    d5 = hashlib.md5()
    d5.update(content.encode(encoding=encoding))  # update添加时会进行计算
    return d5.hexdigest()
