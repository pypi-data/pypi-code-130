# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['formatting', 'labels', 'names']

package_data = \
{'': ['*']}

install_requires = \
['pybtex>=0.24.0,<0.25.0']

entry_points = \
{'pybtex.style.formatting': ['apa7 = formatting.apa:APAStyle'],
 'pybtex.style.labels': ['apa7 = labels.apa:LabelStyle'],
 'pybtex.style.names': ['firstlast = names.firstlast:NameStyle']}

setup_kwargs = {
    'name': 'pybtex-apa7-style',
    'version': '0.1.0',
    'description': 'Provides APA7 style for Pybtex',
    'long_description': None,
    'author': 'Chris Proctor',
    'author_email': 'github.com@accounts.chrisproctor.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
