# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bitbucket_hook_diffstat']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'bitbucket-hook-diffstat',
    'version': '0.1.1',
    'description': '',
    'long_description': '# Bitbucket hook diffstat\n\n## Overview\n\nThis is a simple webhook handler for Bitbucket repository push events.\n\nIt processes branch update and branch create events and extracts the file paths which were changed in that event.\nIn case of branch update event get\'s the changset between current HEAD of the branch and the previous HEAD of that branch.\nIn case if branch is created it get\'s the changset between current HEAD of the branch and HEAD of main branch of the repository.\n\n## Usage\nSet following environment variables:\n```\nBITBUCKET_PROJECT_SLUG\nBITBUCKET_REPO_SLUG\nBITBUCKET_USER\nBITBUCKET_PASSWORD\n```\nWhere `BITBUCKET_PASSWORD` is an "app password" and `BITBUCKET_USER` is available as "Username" in Bitbucket profile settings.\n\nReplace or enhance `class Handler` with your custom logic to trigger some custom CI pipelines for example.\n\nHost it somewhere\n\nCreate the PUSH webhook trigger in your Bitbucket repository.',
    'author': 'Vlad',
    'author_email': 'vova.avdoshka@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
