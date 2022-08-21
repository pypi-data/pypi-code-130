# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fbench']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.2,<2.0.0']

setup_kwargs = {
    'name': 'fbench',
    'version': '0.1.0',
    'description': 'A collection of benchmark functions.',
    'long_description': '<h1 align="center">fBench</h1>\n\n<p align="center">\n<a href="https://pypi.org/project/fbench"><img alt="pypi" src="https://img.shields.io/pypi/v/fbench"></a>\n<a href="https://github.com/estripling/fbench/actions/workflows/release.yml"><img alt="python" src="https://img.shields.io/pypi/pyversions/fbench.svg"></a>\n<a href="https://github.com/estripling/fbench/actions/workflows/release.yml"><img alt="os" src="https://img.shields.io/badge/OS-Ubuntu%2C%20Mac%2C%20Windows-purple"></a>\n<a href="https://github.com/estripling/fbench/blob/main/LICENSE"><img alt="license" src="https://img.shields.io/pypi/l/fbench"></a>\n</p>\n\n<p align="center">\n<a href="https://github.com/estripling/fbench/actions/workflows/ci.yml"><img alt="ci status" src="https://github.com/estripling/fbench/actions/workflows/ci.yml/badge.svg?branch=main"></a>\n<a href="https://github.com/estripling/fbench/actions/workflows/release.yml"><img alt="release" src="https://github.com/estripling/fbench/actions/workflows/release.yml/badge.svg"></a>\n<a href="https://readthedocs.org/projects/fbench/?badge=latest"><img alt="docs" src="https://readthedocs.org/projects/fbench/badge/?version=latest"></a>\n<a href="https://codecov.io/gh/estripling/fbench"><img alt="coverage" src="https://codecov.io/github/estripling/fbench/coverage.svg?branch=main"></a>\n<a href="https://pepy.tech/project/fbench"><img alt="downloads" src="https://pepy.tech/badge/fbench"></a>\n<a href="https://github.com/psf/black"><img alt="black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n<a href="https://pycqa.github.io/isort/"><img alt="isort" src="https://img.shields.io/badge/%20imports-isort-%231674b1&labelColor=ef8336"></a>\n</p>\n\n## About\n\nA collection of benchmark functions.\n\n## Installation\n\n`fbench` is available on [PyPI](https://pypi.org/project/fbench/):\n\n```console\npip install fbench\n```\n\n## Usage\n\n- TODO\n\n## Contributing\n\nInterested in contributing?\nCheck out the [contributing guidelines](https://fbench.readthedocs.io/en/latest/contributing.html) and the [guide for developers](https://fbench.readthedocs.io/en/latest/developers.html).\nPlease note that this project is released with a [Code of Conduct](https://fbench.readthedocs.io/en/latest/conduct.html).\nBy contributing to this project, you agree to abide by its terms.\n\n## License\n\n`fbench` was created by fBench Developers.\nIt is licensed under the terms of the BSD 3-Clause license.\n',
    'author': 'fBench Developers',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/estripling/fbench',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
