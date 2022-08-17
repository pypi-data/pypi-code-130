# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['piconard']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['start = piconard:main']}

setup_kwargs = {
    'name': 'piconard',
    'version': '0.0.3',
    'description': 'Raspberrypi convert to Arduino',
    'long_description': None,
    'author': 'madscientist',
    'author_email': 'eggo.world@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.0,<4.0',
}


setup(**setup_kwargs)
