# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['colabtestingpkg']

package_data = \
{'': ['*']}

install_requires = \
['biopython>=1.70,<2.0',
 'google-api-python-client>=2.42.0,<3.0.0',
 'google-auth>=2.6,<3.0',
 'google-cloud-firestore>=2.4.0,<3.0.0',
 'google-cloud-storage>=2.2.1,<3.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'colabtestingpkg',
    'version': '0.1.4',
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
