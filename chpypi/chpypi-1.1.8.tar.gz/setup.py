#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup, find_packages            #这个包没有的可以pip一下

setup(
    name = "chpypi",      #这里是pip项目发布的名称
    version = "1.1.8",  #版本号，数值大的会优先被pip
    keywords = ["pip", "chpypi"],			# 关键字
    description = "maker's private utils.",	# 描述
    long_description = "maker's private utils.",
    license = "MIT Licence",		# 许可证
    url = "https://www.itax.com",     #项目相关文件地址，一般是github项目地址即可
    author = "maker",			#作者
    author_email = "526548354@qq.com",
    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["requests"]          #这个项目依赖的第三方库
)
