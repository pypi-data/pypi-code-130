# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fairgrad']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.17', 'torch>=1.0']

setup_kwargs = {
    'name': 'fairgrad',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'gmaheshwari',
    'author_email': 'gaurav.maheshwari@inria.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
