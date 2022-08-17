# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ecgai_drawing']

package_data = \
{'': ['*']}

install_requires = \
['pylint>=2.14.5,<3.0.0']

setup_kwargs = {
    'name': 'ecgai-drawing',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'RobC',
    'author_email': 'rob.clapham@gmail.com',
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
