# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['turborequests']
setup_kwargs = {
    'name': 'turborequests',
    'version': '1.0.0',
    'description': 'TurboRequests().get("https://example.com", "status")',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '==3.9.2',
}


setup(**setup_kwargs)
