#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    reshapedata LLC
"""
import platform
from setuptools import setup
from setuptools import find_packages

setup(
    name  ='saveCustomer',
    version = '1.0.5',#版本
    install_requires=[
        'requests',
    ],
    packages=find_packages(),
    license = 'Apache License',
    author='hulilei',
    author_email='hulilei@takewiki.com.cn',
    url = 'http://www.reshapedata.com',
    description = 'reshape data type in py language ',
    keywords = ['reshapedata', 'rdt','pyrdt'],
    python_requires='>=3.6',
)
