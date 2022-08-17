# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['flake8_unused_fixtures']
install_requires = \
['astpretty>=3.0.0,<4.0.0', 'flake8>=5.0.4,<6.0.0']

entry_points = \
{'flake8.extension': ['FUF = flake8_unused_fixtures:Plugin']}

setup_kwargs = {
    'name': 'flake8-unused-fixtures',
    'version': '0.1.0',
    'description': 'Warn about unnecesary fixtures in tests definition.',
    'long_description': None,
    'author': 'Marcin Binkowski',
    'author_email': 'binq661@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MarcinBinkowski/flake8_unused_fixtures',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
