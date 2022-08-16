# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['easy_fossy']

package_data = \
{'': ['*']}

install_requires = \
['pydantic==1.8.2', 'requests-toolbelt==0.9.1', 'requests==2.26.0']

setup_kwargs = {
    'name': 'easy-fossy',
    'version': '2.0.4',
    'description': '',
    'long_description': None,
    'author': 'Ravi Dinesh',
    'author_email': 'dineshr93@gmail.com',
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
