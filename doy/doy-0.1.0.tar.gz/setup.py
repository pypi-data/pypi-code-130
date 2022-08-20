# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['doy', 'doy..ipynb_checkpoints']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'doy',
    'version': '0.1.0',
    'description': '',
    'long_description': '# Doy\n\nSimple utility package\n',
    'author': 'Dominik Schmidt',
    'author_email': 'schmidtdominik30@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
