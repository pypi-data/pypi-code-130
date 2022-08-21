# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['audit_version']

package_data = \
{'': ['*']}

install_requires = \
['cmdkit>=2.6.1,<3.0.0']

entry_points = \
{'console_scripts': ['audit-version = audit_version:main']}

setup_kwargs = {
    'name': 'audit-version',
    'version': '0.1.0',
    'description': 'Audit public interface for Python projects and suggest next semantic version',
    'long_description': "Audit-Version\n=============\n\nAutomatically generate manifest for your Python project's public interface\nand suggest the next semantic version.\n\n",
    'author': 'Geoffrey Lentner',
    'author_email': 'glentner@purdue.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://audit-version.readthedocs.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
