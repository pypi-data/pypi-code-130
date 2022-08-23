#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File     : setup
# @Author   : Mihuier
# @Time     : 2022/8/18 11:22

from distutils.core import  setup
import setuptools
packages = ['AlarmConvergence']# 唯一的包名，自己取名
setup(name='AlarmConvergence',
    version='2.0',
    author='hmh',
    packages=packages, 
    package_dir={'requests': 'requests'},)
