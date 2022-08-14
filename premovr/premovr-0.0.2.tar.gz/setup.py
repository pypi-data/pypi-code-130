# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['premovr', 'premovr.game_interfaces', 'premovr.hardware_interfaces']

package_data = \
{'': ['*']}

install_requires = \
['python-chess>=1.999,<2.0', 'python-lichess>=0.10,<0.11']

entry_points = \
{'console_scripts': ['premovr = premovr.entrypoint:main']}

setup_kwargs = {
    'name': 'premovr',
    'version': '0.0.2',
    'description': 'This is a python library to talk to robot arms to control a chessboard',
    'long_description': None,
    'author': 'Karan Vivek Bhargava',
    'author_email': 'karan.bhargava93@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
