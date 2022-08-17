# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dirdesc']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.1.3,<9.0.0',
 'mypy>=0.971,<0.972',
 'pylint>=2.14.5,<3.0.0',
 'rich>=12.5.1,<13.0.0',
 'types-PyYAML>=6.0.11,<7.0.0']

entry_points = \
{'console_scripts': ['dirdesc = dirdesc.dirdesc:dirdesc']}

setup_kwargs = {
    'name': 'dirdesc',
    'version': '0.1.0',
    'description': 'Generate an annotated directory tree description',
    'long_description': None,
    'author': 'Noah Pendleton',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
