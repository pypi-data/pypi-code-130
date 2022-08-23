# -*- coding = utf-8 -*-
# @Time : 2022-08-01 15:02
# @Author : 王铁翰
# @File : setup.py
# @Software : PyCharm
from setuptools import setup

setup(
    name = 'wthtest',
    version = '0.1.1.4',
    description = 'This is a test lib',
    packages = ['wthtest','sphinxcontrib'],
    namespace_package = ['google'],
    py_modules = ['tool'],
    author = 'wth'
)