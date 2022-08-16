# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['language_detector_api']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp==3.6.2',
 'async-timeout==3.0.1',
 'fasttext==0.9.2',
 'typing-extensions==3.7.4.3',
 'uvloop==0.14.0']

setup_kwargs = {
    'name': 'language-detector-api',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
