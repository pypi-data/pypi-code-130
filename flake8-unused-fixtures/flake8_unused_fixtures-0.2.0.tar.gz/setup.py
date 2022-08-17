# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['flake8_unused_fixtures']
install_requires = \
['astunparse>=1.6.3,<2.0.0', 'flake8>=5.0.4,<6.0.0']

entry_points = \
{'flake8.extension': ['FUF = flake8_unused_fixtures:Plugin']}

setup_kwargs = {
    'name': 'flake8-unused-fixtures',
    'version': '0.2.0',
    'description': 'Warn about unnecesary fixtures in tests definition.',
    'long_description': '# flake8_unused_fixtures\nThis project searches for all functions \nwith prefix "test_" or suffix "_test" \nand searches for all unused fixture names inside the function body.\nFor now, it does not check if the function is actually marked as fixture. ',
    'author': 'Marcin Binkowski',
    'author_email': 'binq661@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MarcinBinkowski/flake8_unused_fixtures',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
