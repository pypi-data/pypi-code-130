# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hyperfocus',
 'hyperfocus.config',
 'hyperfocus.console',
 'hyperfocus.console.commands',
 'hyperfocus.console.core',
 'hyperfocus.database',
 'hyperfocus.services',
 'hyperfocus.termui']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'peewee>=3.15.1,<4.0.0', 'pyperclip>=1.8.2,<2.0.0']

entry_points = \
{'console_scripts': ['hyf = hyperfocus.console.cli:run']}

setup_kwargs = {
    'name': 'hyperfocus',
    'version': '1.0.0a1',
    'description': 'Minimalist task manager.',
    'long_description': '<p align="center">\n    <a href="#readme">\n        <img alt="HyperFocus logo" src="https://raw.githubusercontent.com/u8slvn/hyperfocus/main/_statics/logo.png">\n    </a>\n</p>\n<p align="center">\n    <a href="https://pypi.org/project/hyperfocus/"><img src="https://img.shields.io/pypi/v/hyperfocus.svg" alt="Pypi Version"></a>\n    <a href="https://pypi.org/project/hyperfocus/"><img src="https://img.shields.io/pypi/pyversions/hyperfocus" alt="Python Version"></a>\n    <a href="https://github.com/u8slvn/hyperfocus/actions/workflows/ci.yml"><img src="https://img.shields.io/github/workflow/status/u8slvn/hyperfocus/CI/main" alt="CI"></a>\n    <a href="https://coveralls.io/github/u8slvn/hyperfocus?branch=main"><img src="https://coveralls.io/repos/github/u8slvn/hyperfocus/badge.svg?branch=main" alt="Coverage Status"></a>\n    <a href="https://app.codacy.com/gh/u8slvn/hyperfocus/dashboard"><img src="https://img.shields.io/codacy/grade/01ddd5668dbf4fc09f20ef215d0eec0b" alt="Code Quality"></a>\n    <a href="https://pypi.org/project/hyperfocus/"><img src="https://img.shields.io/pypi/l/hyperfocus" alt="Project license"></a>\n</p>\n\n---\n\n```shell\n$ pipx install hyperfocus --pip-args="--pre"\n```\n',
    'author': 'u8slvn',
    'author_email': 'u8slvn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/u8slvn/hyperfocus',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
