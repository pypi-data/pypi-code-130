# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['loganalyst']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.2,<3.0.0', 'termcolor>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['loga = loganalyst.cli:run']}

setup_kwargs = {
    'name': 'loganalyst',
    'version': '1.0.2',
    'description': 'Analyse some log files',
    'long_description': None,
    'author': 'fdev31',
    'author_email': 'fdev31@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
