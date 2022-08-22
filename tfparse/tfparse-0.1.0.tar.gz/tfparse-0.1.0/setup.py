# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tfparse']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tfparse',
    'version': '0.1.0',
    'description': 'Terraform HCL Parser',
    'long_description': None,
    'author': 'Stacklet',
    'author_email': 'info@stacklet.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
