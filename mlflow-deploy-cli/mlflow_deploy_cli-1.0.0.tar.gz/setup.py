# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mlflow_deploy_cli', 'mlflow_deploy_cli.utils']

package_data = \
{'': ['*'], 'mlflow_deploy_cli': ['template/*']}

install_requires = \
['prompt-toolkit>=3.0.30,<4.0.0']

setup_kwargs = {
    'name': 'mlflow-deploy-cli',
    'version': '1.0.0',
    'description': '',
    'long_description': None,
    'author': 'Aleksandar Ivanovski',
    'author_email': 'aleksandar.ivanovski@codechem.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
