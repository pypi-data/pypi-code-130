# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tabulator_webuntis_ap']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'click>=8.1.3,<9.0.0', 'webuntis>=0.1.12,<0.2.0']

entry_points = \
{'console_scripts': ['tabulate-webuntis-ap = '
                     'tabulator_webuntis_ap.main:tabulate']}

setup_kwargs = {
    'name': 'tabulator-webuntis-ap',
    'version': '0.3.0',
    'description': '',
    'long_description': None,
    'author': 'Vincent Nys',
    'author_email': 'vincent.nys@ap.be',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
