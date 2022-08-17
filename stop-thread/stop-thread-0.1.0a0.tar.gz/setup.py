# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stop_thread']

package_data = \
{'': ['*']}

install_requires = \
['logzero>=1.7.0,<2.0.0']

entry_points = \
{'console_scripts': ['stop-thread = stop_thread.__main__:app']}

setup_kwargs = {
    'name': 'stop-thread',
    'version': '0.1.0a0',
    'description': 'Stop a thread in a nasty way',
    'long_description': '# stop-thread\n[![pytest](https://github.com/ffreemt/stop-thread/actions/workflows/routine-tests.yml/badge.svg)](https://github.com/ffreemt/stop-thread/actions)[![python](https://img.shields.io/static/v1?label=python+&message=3.8%2B&color=blue)](https://www.python.org/downloads/)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/stop_thread.svg)](https://badge.fury.io/py/stop_thread)\n\nStop a thread in a nasty way\n\n## Install it\n\n```shell\npip install stop_thread\n# pip install git+https://github.com/ffreemt/stop-thread\n# poetry add git+https://github.com/ffreemt/stop-thread\n# git clone https://github.com/ffreemt/stop-thread && cd stop-thread\n```\n\n## Use it\n```python\nimport threading\nfrom stop_thread import stop_thread\n\nident = threading.current_thread().ident\nstop_thread(ident)\n# possibly follow up with some clean-up to properly terminate the thread\n# e.g. thread.quit(); thread.wait()\n```\n',
    'author': 'ffreemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/stop-thread',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.3,<4.0.0',
}


setup(**setup_kwargs)
