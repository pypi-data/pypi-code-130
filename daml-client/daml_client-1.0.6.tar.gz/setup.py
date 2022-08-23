# -*- coding: UTF-8 -*-
import os
 
import setuptools
with open("README.md","r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='daml_client',
    version="1.0.6",
    keywords='demo',
    description='A demo for python packaging.',
    long_description=open(
        os.path.join(
            os.path.dirname(__file__),
            'README.rst'
        )
    ).read(),
    author='yut-75',      # 替换为你的Pypi官网账户名
    author_email='xiao3952@foxmail.com',  # 替换为你Pypi账户名绑定的邮箱
 
    url='https://github.com/xxx',   # 这个地方为github项目地址，貌似非必须
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],  # 这个文件适用的python版本，安全等等，我这里只写入了版本
    license='MIT'
)