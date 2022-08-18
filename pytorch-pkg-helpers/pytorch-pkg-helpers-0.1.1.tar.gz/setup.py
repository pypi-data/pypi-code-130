# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytorch_pkg_helpers']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['pytorch_pkg_helper = pytorch_pkg_helpers.__main__:main']}

setup_kwargs = {
    'name': 'pytorch-pkg-helpers',
    'version': '0.1.1',
    'description': 'Tool to determine pytorch dependencies for common domain library use cases',
    'long_description': None,
    'author': 'Eli Uriegas',
    'author_email': 'eliuriegas@fb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
