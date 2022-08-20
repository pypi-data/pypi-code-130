# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xterm256_colors']

package_data = \
{'': ['*']}

modules = \
['LICENSE', 'CHANGELOG']
extras_require = \
{'colormath': ['colormath>=3.0.0,<4.0.0']}

setup_kwargs = {
    'name': 'xterm256-colors',
    'version': '0.1.2',
    'description': 'Handy utilities for interacting with xterm-256color terminal emulators',
    'long_description': "# xterm256-colors\n\n[![PyPI version](https://badge.fury.io/py/xterm256-colors.svg)](https://badge.fury.io/py/xterm256-colors)\n\nEasily colorize text printed to an xterm-256color terminal emulator\n\n```python\nfrom xterm256_colors import Fore256, Back256\n\nprint(Fore256.CHARTREUSE1('Hello,'), Back256.HOTPINK('World!'))\n```\n\n![Screenshot of example code output](.images/xterm256-colors-example.png)\n\n\n# Installation\n```shell\npip install xterm256-colors\n```\n",
    'author': 'Zach "theY4Kman" Kanzler',
    'author_email': 'they4kman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theY4Kman/xterm256-colors',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
