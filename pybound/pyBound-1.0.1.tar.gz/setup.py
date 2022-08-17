# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pybound']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pybound',
    'version': '1.0.1',
    'description': 'pyBound is a collection of useful functions that can be used in many situations in python files.',
    'long_description': None,
    'author': "Xhaiden D'Souza",
    'author_email': 'xhaidendsouza@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
