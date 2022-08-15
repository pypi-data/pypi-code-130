# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['weiroll']
install_requires = \
['eth-brownie>=v1.17,<2.0']

setup_kwargs = {
    'name': 'weiroll-py',
    'version': '0.2.0',
    'description': 'Build weiroll transactions with brownie',
    'long_description': None,
    'author': 'FP',
    'author_email': 'FP@no-email.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
