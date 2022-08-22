# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qldebugger', 'qldebugger.actions', 'qldebugger.config', 'qldebugger.example']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.24,<2.0', 'click>=8.1,<9.0', 'pydantic>=1.9,<2.0', 'tomli>=2.0,<3.0']

entry_points = \
{'console_scripts': ['qldebugger = qldebugger.cli:cli']}

setup_kwargs = {
    'name': 'qldebugger',
    'version': '0.1.0',
    'description': 'Utility to debug AWS lambdas with SQS messages',
    'long_description': '# Queue Lambda Debugger\n\nUtility to debug AWS lambdas with SQS messages.\n',
    'author': 'Eduardo Klosowski',
    'author_email': 'eduardo_klosowski@yahoo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/eduardoklosowski/qldebugger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
