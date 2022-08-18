# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deepviewcore',
 'deepviewcore.filters',
 'deepviewcore.process',
 'deepviewcore.tests']

package_data = \
{'': ['*']}

install_requires = \
['numpy', 'opencv-python']

entry_points = \
{'console_scripts': ['test = deepviewcore.shell:start']}

setup_kwargs = {
    'name': 'deepviewcore',
    'version': '0.1.6',
    'description': '',
    'long_description': None,
    'author': 'Miguel Martín',
    'author_email': 'alu0101209777@ull.edu.es',
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
