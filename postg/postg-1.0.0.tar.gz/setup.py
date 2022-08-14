# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['postg']
setup_kwargs = {
    'name': 'postg',
    'version': '1.0.0',
    'description': 'None',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
