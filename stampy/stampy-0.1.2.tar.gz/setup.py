# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stampy']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0', 'click>=8.1.3,<9.0.0']

entry_points = \
{'console_scripts': ['stampy = stampy.main:main']}

setup_kwargs = {
    'name': 'stampy',
    'version': '0.1.2',
    'description': '４文字の文字列をスタンプ風画像に変換するツール ',
    'long_description': None,
    'author': 'Comamoca',
    'author_email': 'comamoca.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
