# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['my_fetchers']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4==4.10.0', 'requests==2.26.0']

setup_kwargs = {
    'name': 'my-fetchers',
    'version': '0.1.0',
    'description': 'Web Scrapper',
    'long_description': None,
    'author': 'ehsan.tavan',
    'author_email': 'ehsan.tavan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
