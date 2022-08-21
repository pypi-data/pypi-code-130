# coding=utf-8

import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup (
    name = 'gragal',
    version = '0.1.0',
    description = 'Gragal API Client',
    long_description = 'With this official Python client you can plug into the power and speed of Gragal Image Optimizer.',
    url = 'https://github.com/gragal/gragal-python',
    author = 'Yonamco',
    author_email = 'support@kraken.io',
    license = 'MIT',
    keywords = 'Gragal image optimizer optimiser resizer',

    packages = [
        'gragal'
    ],

    install_requires = [
        'requests'
    ],

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ]
)
