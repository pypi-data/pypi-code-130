# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_jsonl_loader']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.6.0,<0.7.0']

setup_kwargs = {
    'name': 'py-jsonl-loader',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'Philip Huang',
    'author_email': 'p208p2002@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
