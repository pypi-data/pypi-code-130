# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['anton_test']
setup_kwargs = {
    'name': 'anton-test',
    'version': '2.0.0',
    'description': 'ask func',
    'long_description': None,
    'author': 'Skazko Anton',
    'author_email': 'sk.anton06@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
