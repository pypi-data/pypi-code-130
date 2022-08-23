# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiodeu']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.24.57,<2.0.0',
 'faust-streaming>=0.8.5,<0.9.0',
 'python-schema-registry-client>=2.4.0,<3.0.0']

entry_points = \
{'console_scripts': ['aiodeu = aiodeu.console:main']}

setup_kwargs = {
    'name': 'aiodeu',
    'version': '0.1.14',
    'description': 'aio data engineering utils',
    'long_description': None,
    'author': 'Josh Rowe',
    'author_email': 's-block@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/s-block/aiodeu',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
