# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arguments']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=4.1.1,<5.0.0']

setup_kwargs = {
    'name': 'tombulled-arguments',
    'version': '0.1.5',
    'description': 'Arguments manager',
    'long_description': None,
    'author': 'Tom Bulled',
    'author_email': '26026015+tombulled@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
