# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oyabun', 'oyabun.telegram']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp[speedups]>=3.8.1,<4.0.0',
 'orjson>=3.7.11,<4.0.0',
 'pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'oyabun',
    'version': '2022.8.20.dev6',
    'description': 'Telegram library with strict API',
    'long_description': "# 親分\n\n_— the extreme path_\n\nA library for building Telegram bots.\n\n![shimizu no jirocho](https://github.com/tgrx/oyabun/raw/main/docs/img/shimizu_no_jirocho.jpg)\n\n![build status](https://github.com/tgrx/oyabun/actions/workflows/development.yaml/badge.svg?branch=main)\n\n## Mission\n\nThe mission of this library is to provide a strict interface for the API.\nBy *strict* we mean that all types and methods in the library interface\nare mapped to those described in the Telegram API docs.\n\nYou won't meet any auxiliary stuff like sophisticated OOP/async patterns,\nobscure event loops and listeners and the kind of stuff like that.\n\nAPI types are Pydantic models with strict type hints.\n\nAPI methods accept params with exactly the same type and name as described in API.\n\nAny optional field/param is marked as `Optional` or `None | T`. Don't be afraid of tri-state bool types.\n",
    'author': 'Alexander Sidorov',
    'author_email': 'alexander@sidorov.dev',
    'maintainer': 'Alexander Sidorov',
    'maintainer_email': 'alexander@sidorov.dev',
    'url': 'https://github.com/tgrx/oyabun',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
