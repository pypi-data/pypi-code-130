#!/usr/bin/env python

import sys

from setuptools import setup

with open('README.rst', 'r') as readme:
    long_description = readme.read()

setup(
    name='wagtail-rps-template',
    version='1.0.2',
    author='Manuel Schiegg',
    author_email='pypi@schiegg.at',
    url='https://github.com/red-pepper-services/wagtail-rps-template',
    license='MIT',
    description="Wagtail Admin customising for red pepper Customer",
    long_description=long_description,
    include_package_data=True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Wagtail',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)