# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sparrow_flir']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0', 'numpy>=1.23.2,<2.0.0']

setup_kwargs = {
    'name': 'sparrow-flir',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Sparrow Computing',
    'author_email': 'ben@sparrow.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
