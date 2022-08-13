# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['astrolog']

package_data = \
{'': ['*']}

install_requires = \
['dms2dec>=0.1,<0.2', 'pyswisseph==2.10.02.0.dev1']

setup_kwargs = {
    'name': 'astrolog',
    'version': '0.5.0',
    'description': 'High-level astrology methods based on Swiss Ephemeris',
    'long_description': None,
    'author': 'Ign. Aiom Ominous',
    'author_email': 'aiom.ominous@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
