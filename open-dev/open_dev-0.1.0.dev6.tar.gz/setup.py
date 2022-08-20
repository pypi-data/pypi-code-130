# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['open_dev', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['click==8.0.1', 'yamllint>=1.27.1,<2.0.0']

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0',
         'bump2version>=1.0.1,<2.0.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocs-material>=6.1.7,<7.0.0',
         'mkdocstrings>=0.15.2,<0.16.0',
         'mkdocs-autorefs>=0.2.1,<0.3.0'],
 'test': ['black>=21.5b2,<22.0',
          'isort>=5.8.0,<6.0.0',
          'flake8>=3.9.2,<4.0.0',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'mypy>=0.900,<0.901',
          'pytest>=6.2.4,<7.0.0',
          'pytest-cov>=2.12.0,<3.0.0']}

entry_points = \
{'console_scripts': ['open_dev = open_dev.cli:main']}

setup_kwargs = {
    'name': 'open-dev',
    'version': '0.1.0.dev6',
    'description': 'A collection of tooling to enable open source development..',
    'long_description': '# open_dev\n\n\n[![pypi](https://img.shields.io/pypi/v/open_dev.svg)](https://pypi.org/project/open_dev/)\n[![python](https://img.shields.io/pypi/pyversions/open_dev.svg)](https://pypi.org/project/open_dev/)\n[![Build Status](https://github.com/8ball030/open_dev/actions/workflows/dev.yml/badge.svg)](https://github.com/8ball030/open_dev/actions/workflows/dev.yml)\n[![codecov](https://codecov.io/gh/8ball030/open_dev/branch/main/graphs/badge.svg)](https://codecov.io/github/8ball030/open_dev)\n\n\nInstall Dependencies.\n\n(Poetry) Is used to managed the dependencies. (https://python-poetry.org/docs/#installation)\n# osx / linux / bashonwindows install instructions\n```bash\ncurl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -\n```\n```\n# windows install instructions\n```\n```\n(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python `\n```\n\n\nA collection of tooling to enable open source development.\n\n\n* Documentation: <https://8ball030.github.io/open_dev>\n* GitHub: <https://github.com/8ball030/open_dev>\n* PyPI: <https://pypi.org/project/open_dev/>\n* Free software: Apache-2.0\n\n\n## Features\n\n* TODO\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.\n',
    'author': '8Baller',
    'author_email': '8ball030@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/8ball030/open_dev',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
