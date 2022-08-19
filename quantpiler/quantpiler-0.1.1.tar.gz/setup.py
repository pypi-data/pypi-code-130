# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quantpiler']

package_data = \
{'': ['*']}

install_requires = \
['qiskit>=0.37.1,<0.38.0']

setup_kwargs = {
    'name': 'quantpiler',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'AveryanAlex',
    'author_email': 'alex@averyan.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
