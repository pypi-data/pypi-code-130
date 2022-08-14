# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['motical', 'motical.aux', 'motical.data']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'motical',
    'version': '0.1.0',
    'description': 'Motivational Life Calendar',
    'long_description': '# Motical - Motivational Calendar\n\n[![PyPI Version][pypi-image]][pypi-url]\n[![Build Status][build-image]][build-url]\n[![Code Coverage][coverage-image]][coverage-url]\n[![][stars-image]][stars-url]\n[![][versions-image]][versions-url]\n\nIt could be a harsh way to motivate yourself but this Python package/app \nwill help you to understand were in your lifetime you are.\n\nBased on avarage lifespan of a person in specific country (in future - based on other life conditions)\nyou may get your "life calendar" with number of weeks, years already passed and yet to go ...\n\n\n<!-- Badges: -->\n\n[pypi-image]: https://img.shields.io/pypi/v/motical\n[pypi-url]: https://pypi.org/project/motical/\n[build-image]: https://github.com/mathspp/motical/actions/workflows/build.yaml/badge.svg\n[build-url]: https://github.com/mathspp/motical/actions/workflows/build.yaml\n[coverage-image]: https://codecov.io/gh/mathspp/motical/branch/main/graph/badge.svg\n[coverage-url]: https://codecov.io/gh/mathspp/motical/\n[stars-image]: https://img.shields.io/github/stars/mathspp/motical/\n[stars-url]: https://github.com/mathspp/motical\n[versions-image]: https://img.shields.io/pypi/pyversions/motical/\n[versions-url]: https://pypi.org/project/motical/\n',
    'author': 'Max Ligus',
    'author_email': 'max.ligus@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
