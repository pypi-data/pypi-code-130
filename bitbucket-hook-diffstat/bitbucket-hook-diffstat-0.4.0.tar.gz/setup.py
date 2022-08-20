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
    'version': '0.4.0',
    'description': 'Bitbucket push webhook handler to generate a list of files changed on a push',
    'long_description': '# Bitbucket hook diffstat\n\n## Overview\n\nBitbucket push webhook handler to generate a list of files changed on a push.\n\nIt processes branch updates, and the branch creates events and extracts the file paths of the files whose content was changed in that event, including the removal or creation of the file itself.\nIn the case of a branch update event, it gets the changeset between the current HEAD of the branch and the previous HEAD of that branch.\nIn case the branch is created, it gets the changeset between the current HEAD of the branch and the HEAD of the main branch of the repository.\nIt uses Bitbucket `diffstat`,  `repositories`, and `branches` APIs. It handles some basic retries on unexpected HTTP response codes from BitBucket.\n\n## Usage\n```python\nfrom bitbucket_hook_diffstat import process_bitbucket_push_events\n\nresult = process_bitbucket_push_events(\n    push_payload, repo_owner, repo_name, bitbucket_user, bitbucket_password\n) # it might raise an Exception, please check `bitbucket_hook_diffstat/exceptions.py`\n\nresult # Is a dict of a zero or more branch names - strings to the set of one or many file pathnames - strings.\n{\'master\': {\'.gitignore\'}}\n```\n\n`push_payload` is a Bitbucket repository [push event](https://support.atlassian.com/bitbucket-cloud/docs/event-payloads/#Push)\n\n`repo_owner` and `repo_name` one can retrieve from the repository URL `https://bitbucket.org/repo_owner/repo_name` \n\n`bitbucket_password` is an "app password" and `bitbucket_user` is available as "Username" in Bitbucket profile settings. This user should be authorized to do Repositories Read.',
    'author': 'Vlad',
    'author_email': 'vova.avdoshka@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vavdoshka/bitbucket-hook-diffstat',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
