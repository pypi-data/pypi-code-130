#!/usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author:lenovo
@file: setup.py
@time: 2022/8/15  15:35
"""
import setuptools

setuptools.setup(
    name="django_feishu_sdk",  # Replace with your own username
    version="0.0.4",
    author="lpf_andr",
    author_email="lpf_andr@163.com",
    description="A feishu api package for django",
    long_description="这是一个用于和飞书开放平台交互的python库,主要用于django框架，对数据和事件进行了封装,并且可以根据需要自行扩展。",
    long_description_content_type="text/markdown",
    url="https://github.com/lpfandr/django_feishu_sdk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
