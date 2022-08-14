# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['startfile', 'startfile.tests']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['universal-startfile = startfile.cli:main']}

setup_kwargs = {
    'name': 'universal-startfile',
    'version': '0.0.1',
    'description': 'A cross-platform version of `os.startfile` from the standard library.',
    'long_description': '# Overview\n\nA cross-platform version of [os.startfile](https://docs.python.org/3/library/os.html#os.startfile) from the standard library.\n\n[![Unix Build Status](https://img.shields.io/github/workflow/status/jacebrowning/universal-startfile/main)](https://github.com/jacebrowning/universal-startfile/actions)\n[![Windows Build Status](https://img.shields.io/appveyor/ci/jacebrowning/universal-startfile.svg?label=windows)](https://ci.appveyor.com/project/jacebrowning/universal-startfile)\n[![Coverage Status](https://img.shields.io/codecov/c/gh/jacebrowning/universal-startfile)](https://codecov.io/gh/jacebrowning/universal-startfile)\n[![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/g/jacebrowning/universal-startfile.svg)](https://scrutinizer-ci.com/g/jacebrowning/universal-startfile)\n[![PyPI License](https://img.shields.io/pypi/l/universal-startfile.svg)](https://pypi.org/project/universal-startfile)\n[![PyPI Version](https://img.shields.io/pypi/v/universal-startfile.svg)](https://pypi.org/project/universal-startfile)\n[![PyPI Downloads](https://img.shields.io/pypi/dm/universal-startfile.svg?color=orange)](https://pypistats.org/packages/universal-startfile)\n\n## Setup\n\n### Requirements\n\n* Python 3.7+\n\n### Installation\n\nInstall it directly into an activated virtual environment:\n\n```text\n$ pip install universal-startfile\n```\n\nor add it to your [Poetry](https://poetry.eustace.io/) project:\n\n```text\n$ poetry add universal-startfile\n```\n\n## Usage\n\nAfter installation, import the `startfile` function:\n\n```python\nfrom startfile import startfile\n\nstartfile("~/Downloads/example.png")\nstartfile("http://example.com")\n```\n',
    'author': 'Jace Browning',
    'author_email': 'jacebrowning@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/startfile',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
