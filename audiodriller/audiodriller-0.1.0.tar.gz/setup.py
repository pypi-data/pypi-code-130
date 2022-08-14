# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['audiodriller']

package_data = \
{'': ['*']}

install_requires = \
['PyInputPlus>=0.2.12,<0.3.0',
 'click>=8.1.3,<9.0.0',
 'dataclasses-json>=0.5.7,<0.6.0',
 'pydub>=0.25.1,<0.26.0',
 'rich>=12.5.1,<13.0.0',
 'simpleaudio>=1.0.4,<2.0.0']

setup_kwargs = {
    'name': 'audiodriller',
    'version': '0.1.0',
    'description': 'A tool for structured, efficient ear training using real recorded audio.',
    'long_description': None,
    'author': 'Vincent Nys',
    'author_email': 'vincentnys@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
