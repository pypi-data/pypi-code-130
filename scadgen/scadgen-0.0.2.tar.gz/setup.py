# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['scadgen']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'scadgen',
    'version': '0.0.2',
    'description': 'A Python library for generating OpenSCAD 3D models.',
    'long_description': '# scadgen\n\nA Python library for generating OpenSCAD 3D models.\n\n',
    'author': 'TC Teo',
    'author_email': 'scadgen-pypi-011ecc47@tsechin.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tcteo/scadgen',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
