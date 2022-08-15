#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="chpypi",
    version="1.1.2",
    author="maker",
    author_email="c13826564630@163.com",
    url="https://www.itaxs.com/",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "requests==2.25.1",
    ],
)