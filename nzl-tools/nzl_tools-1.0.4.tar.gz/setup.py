#!D:/Code/python
# -*- coding: utf-8 -*-
# @Time :2022/1/6 9:06
# @Author : NZL
# @File : setup.py.py
# @Desc :
import setuptools

universal = 2

setuptools.setup(
    name="nzl_tools",
    version="1.0.4",
    author="nzl",
    author_email="nzl0379@163.com",
    description="工具包",
    packages=setuptools.find_packages()
)

# python setup.py sdist  打包命令
# python setup.py sdist bdist_wheel --universal 打包命令
# python -m twine upload dist/*   上传命令
