# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clean_rst']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.27,<4.0.0', 'restructuredtext-lint>=1.4.0,<2.0.0']

entry_points = \
{'console_scripts': ['clean-rst = clean_rst.main:main']}

setup_kwargs = {
    'name': 'clean-rst',
    'version': '0.1.0',
    'description': 'pre-commit to clean rst index files',
    'long_description': None,
    'author': 'Bertrand Benjamin',
    'author_email': 'benjamin.bertrand@opytex.org',
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
