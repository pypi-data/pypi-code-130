# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bibliothek']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.2,<3.0.0',
 'typer[all]>=0.6.1,<0.7.0',
 'urllib3>=1.26.12,<2.0.0']

entry_points = \
{'console_scripts': ['bibliothek = bibliothek.__main__:app']}

setup_kwargs = {
    'name': 'papermc-bibliothek',
    'version': '4.0.1',
    'description': 'bibliothek API client with CLI',
    'long_description': '# papermc-bibliothek\n\npythonic [bibliothek](https://github.com/PaperMC/bibliothek) API wrapper with a CLI\n\n## Installation\n\npapermc-bibliothek requires python 3.9 or above\n\n```shell\n# PIP3\npip3 install papermc-bibliothek\n# PIP\npip install papermc-bibliothek\n```\n\n## API\n\nAll functions and classes are properly type hinted and documented with triple quotes. Please file an issue or pull\nrequest with any corrections if any issues are found.\n\n### Basic Usage\n\n```python\nfrom bibliothek import Bibliothek, BibliothekException\n\nbibliothek = Bibliothek()  # Create an instance of the Bibliothek class\ntry:\n    projects = bibliothek.get_projects()\n    print(projects)  # [\'paper\', \'travertine\', \'waterfall\', \'velocity\']\nexcept BibliothekException as e:  # Catch BibliothekException in case something goes wrong\n    print(f"Error: {e}")\n```\n\n## CLI\n\nWill generally contain most features of the API<!--, use (the secret project) for proper server managment-->.\n\n```shell\nUsage: bibliothek [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  download-build\n  get-build\n  get-project\n  get-projects\n  get-version\n  get-version-group\n  get-version-group-builds\n```',
    'author': 'Oskar',
    'author_email': '56176746+OskarZyg@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/OskarsMC-Network/papermc-bibliothek',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
