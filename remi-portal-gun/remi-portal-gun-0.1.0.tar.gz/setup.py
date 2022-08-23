# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['remi_portal_gun']

package_data = \
{'': ['*']}

install_requires = \
['typer>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['remi-portal-gun = remi_portal_gun.main:app']}

setup_kwargs = {
    'name': 'remi-portal-gun',
    'version': '0.1.0',
    'description': '',
    'long_description': "I'm attempting to push a package on pypy \n",
    'author': 'Rémi Connesson',
    'author_email': 'remiconnesson@gmail.com',
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
