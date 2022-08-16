# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dramatiq_mongodb']

package_data = \
{'': ['*']}

install_requires = \
['dramatiq>=1.12.1,<2.0.0', 'pymongo>=4.1,<5']

setup_kwargs = {
    'name': 'dramatiq-mongodb',
    'version': '0.6.2',
    'description': 'Dramatiq-Mongodb Broker and Results Backend for Dramatiq',
    'long_description': "# Dramatiq-Mongodb Broker and Results Backend for Dramatiq\n\n| :exclamation: _WARNING_ This is very early beta software that has not yet been proven to work. :exclamation: |\n| ------------------------------------------------------------------------------------------------------------ |\n\n![CI/CD Pipeline](https://img.shields.io/github/workflow/status/obscuritylabs/dramatiq-mongodb/CI-CD/main?label=CI/CD)\n\n![Latest SEMVER](https://img.shields.io/github/v/tag/obscuritylabs/dramatiq-mongodb)\n\n## Usage Instructions\n\n## Development Instructions\n\n### Configure development environment\n\nInstall Development Dependencies using Poetry:\n\n```shell\npoetry install\n```\n\nInstall githooks to automate quality checks locally:\n\n```shell\npoetry run pre-commit install --install-hooks -t pre-commit -t commit-msg\n```\n\n### Run code quality checks locally\n\nAll code quality checks are performed using the Makefile at the root of the repository. You can execute individual steps by name or execute all steps by omitting a target using `make` or specifying `make all`:\n\n```shell\nmake all\n```\n\nIf you want to purge the repo of all ignore files include the embedded virtual environment then run all tests in a fresh environment you can run:\n\n```shell\nmake clean all\n```\n\nChangelog and semantic version are automated using [Semantic-Release](https://python-semantic-release.readthedocs.io/en/latest/) during the CD process. To accomplish this, this repository makes heavy use of [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), thought this isn't strictly enforced on the server side at this time until 1.0 is released, but the githooks will lint your commits.\n\n### Start a local MongoDB\n\n```shell\ndocker run -d -p 27017:27017 --name mongo -e MONGO_INITDB_ROOT_USERNAME=username -e MONGO_INITDB_ROOT_PASSWORD=password mongo\n```\n\nOnce the mongodb server is up and running you can create a pymongo client and pass it either into a MongoDBBroker or a MongoDBBackend to test the code locally. Otherwise everything should behave in accordance with the documentation for [Dramatiq](https://dramatiq.io/).\n",
    'author': 'Tory Clasen',
    'author_email': 'ToryClasen@Gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/obscuritylabs/dramatiq-mongodb',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
