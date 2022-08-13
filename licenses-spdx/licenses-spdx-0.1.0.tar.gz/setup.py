# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['src']

package_data = \
{'': ['*']}

modules = \
['licenses_nonobsolete_only']
install_requires = \
['pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'licenses-spdx',
    'version': '0.1.0',
    'description': 'A powerful API to grab spdx list licenses, great for boilerplate gen and way more (not official)',
    'long_description': None,
    'author': 'aarmn',
    'author_email': 'aarmn80@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
