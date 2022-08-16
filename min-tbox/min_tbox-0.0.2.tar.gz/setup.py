#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
  @Author: zhangzongliang
  @Date: 2022-08-09 11:37:54
  @Description:
  @Email: noaghzil@gmail.com
  @Last Modified time: 2022-08-16 17:18:35
"""

from setuptools import find_packages, setup

setup(
    name="min_tbox",
    version="0.0.2",
    description='some kit tool ',
    author='noaghzil',
    author_email='noaghzil@gmail.com',
    packages=find_packages(),
    install_requires=["redis", "pytest", "pytest-asyncio", "aiohttp"],
)
