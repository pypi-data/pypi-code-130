#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File     : setup
# @Author   : Mihuier
# @Time     : 2022/8/18 11:22

import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='HMH_AlarmConvergence',
    version='0.0.1',
    author='Mihuier',
    author_email='1205083785@qq.com',
    description='Oh Bear !',
    long_description=long_description,
    url='https://gitee.com/dino-ding6024/alarm-convergence-1',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

