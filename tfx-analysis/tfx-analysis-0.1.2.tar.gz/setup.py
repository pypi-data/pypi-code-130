# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tfx_analysis']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tfx-analysis',
    'version': '0.1.2',
    'description': '',
    'long_description': None,
    'author': 'ZF Deng',
    'author_email': 'zhifeng.deng@opendoor.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
