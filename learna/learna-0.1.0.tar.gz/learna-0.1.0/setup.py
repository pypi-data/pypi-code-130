# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['learna']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'learna',
    'version': '0.1.0',
    'description': 'Machine learning implemented purely in python. Mainly for research and learning purposes.',
    'long_description': '# learna\nMachine learning library\n',
    'author': 'Naveen Anil',
    'author_email': 'naveenms01@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nvn-nil/learna',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
