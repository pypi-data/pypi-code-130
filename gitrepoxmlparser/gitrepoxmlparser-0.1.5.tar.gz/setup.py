# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gitrepoxmlparser']

package_data = \
{'': ['*']}

install_requires = \
['rich==12.5.1']

entry_points = \
{'console_scripts': ['gitrepoxmlparser = gitrepoxmlparser:main']}

setup_kwargs = {
    'name': 'gitrepoxmlparser',
    'version': '0.1.5',
    'description': 'Provides Details for your GitRepo master manifest file ',
    'long_description': '# GitRepoXMLParser\n\n## _Capable of processing the AOSP repo\'s manifest file differentiating from the supplier_\n\nGitRepoXMLParser helps you visualize your AOSP manifest files that is fed for [repo](https://source.android.com/docs/setup/develop/repo) tool\n[Rich](https://pypi.org/project/rich/)-powered visualization.\n\n## Manifest file example\n\n```sh\n<manifest >\n    <remote fetch = "url" name = "pj-gerrit" review = "" / >\n    <include name = "supplier.xml" / >\n    <include name = "pj_apps.xml" / >\n    <remove-project name = "pathto/projec" / >\n    <project name = "supplier/pathto/projectrepo" path = "company/pathto/projectrepo" remote = "pj-gerrit" revision = "branch_name" / >\n    <project name = "PJ/pathto/projectrepo1" path = "vendor/pathto/projectrepo1" remote = "pj-gerrit" revision = "branch_name" / >\n    <project name = "PJ/pathto/projectrepo2" path = "vendor/pathto/projectrepo2" remote = "pj-gerrit" revision = "branch_name" / >\n</manifest >\n```\n\n## Features\n\n- Visualize your manifest.xml files visually\n- The table size depends on the screensize of the command line utility that you are running the script\n\n## Installation\n\ngitrepoxmlparser requires [Rich](https://pypi.org/project/rich/) 12.5.1+.\n\n```sh\npip install gitrepoxmlparser\n```\n\n## Usage\n\n```sh\ncmd>gitrepoxmlparser -h\nusage: gitrepoxmlparser.exe [-h] -f F -c C -s S\n\noptions:\n  -h, --help  show this help message and exit\n  -f F        manifest xml file\n  -c C        Your company name (Should match with companies folder name in the stack)\n  -s S        Supplier\'s Company name (just contrasts with only one vendor)\n```\n\n#### Building the source\n\nTo activate the virtual env\n\n```sh\npoetry shell\n```\n\nInstalling dependencies only\n\n```sh\npoetry install --no-root\n```\n\nTo install the dependencies and install the package (reads the poetry.lock or pyproject.toml file )\n\n```sh\npoetry install\n```\n\n## License\n\nMIT\n\n**Free Software, Hell Yeah!**\n',
    'author': 'Ravi Dinesh',
    'author_email': 'dineshr93@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
