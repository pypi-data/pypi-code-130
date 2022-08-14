# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['premovr']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'premovr',
    'version': '0.0.1',
    'description': 'This is a python library to talk to robot arms to control a chessboard',
    'long_description': None,
    'author': 'Karan Vivek Bhargava',
    'author_email': 'karan.bhargava93@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
