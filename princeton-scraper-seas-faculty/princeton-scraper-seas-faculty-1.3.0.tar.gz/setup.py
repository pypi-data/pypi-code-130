# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['princeton_scraper_seas_faculty']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0.1,<0.0.2', 'comma==0.5.3', 'requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'princeton-scraper-seas-faculty',
    'version': '1.3.0',
    'description': 'A web scraper that produces JSON feeds directly and automatically from the Princeton SEAS faculty directory.',
    'long_description': None,
    'author': 'Jérémie Lumbroso',
    'author_email': 'lumbroso@cs.princeton.edu',
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
