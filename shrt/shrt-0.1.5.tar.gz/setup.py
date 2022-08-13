# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shrt', 'shrt.cli', 'shrt.views']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.40,<2.0.0',
 'databases[aiosqlite]>=0.6.0,<0.7.0',
 'fastapi-jinja>=0.2.0,<0.3.0',
 'fastapi[all]>=0.79.0,<0.80.0',
 'tabulate>=0.8.10,<0.9.0',
 'typer>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['shrt = shrt.cli.main:cli']}

setup_kwargs = {
    'name': 'shrt',
    'version': '0.1.5',
    'description': 'Shorten URLs',
    'long_description': '# SHRT - Shortened URL service\n\nAn MVP to serve shortened URLs\n\n## Usage\n\nServe using `uvicorn` by running\n\n```shell\nuvicorn --host=0.0.0.0 shrt.web:app\n```\n\nManage URLs from the CLI\n\n```shell\n# List URLs\nshrt url list\n# Create a random short path\nshrt url add https://x59.us\n# Create a custom short path\nshrt url add https://x59.co --path x59\n# Create a new short path, even if the target exists in the DB\nshrt url add https://x59.co --create-new\n# Get details for a given short path\nshrt url get x59\n```\n',
    'author': 'Yehuda Deutsch',
    'author_email': 'yeh@uda.co.il',
    'maintainer': 'Yehuda Deutsch',
    'maintainer_email': 'yeh@uda.co.il',
    'url': 'https://gitlab.com/uda/shrt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
