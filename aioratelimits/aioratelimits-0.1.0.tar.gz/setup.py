# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['aioratelimits']
setup_kwargs = {
    'name': 'aioratelimits',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Dmitry Kostromin',
    'author_email': 'kupec-k@ya.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
