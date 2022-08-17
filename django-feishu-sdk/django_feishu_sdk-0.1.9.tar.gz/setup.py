#!/usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author:lenovo
@file: setup.py
@time: 2022/8/15  15:35
"""
import setuptools

# 导入静态文件
file_data = [
    "README.md",
]
# 自动读取readme
with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()
setuptools.setup(
    name="django_feishu_sdk",  # Replace with your own username
    version="0.1.9",
    author="lpf_andr",
    author_email="lpf_andr@163.com",
    description="A feishu api package for django",
    readme="README.md",
    long_description=readme,
    long_description_content_type="text/markdown",
    data_files=file_data,  # 打包时需要打包的数据文件，如图片，配置文件等
    url="https://gitee.com/li-pf/django_feishu_sdk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=['cryptography', 'pydantic', 'aiohttp', 'requests', 'pycryptodome'],  # 安装所需要的库
)
