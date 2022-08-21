# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yvpn']

package_data = \
{'': ['*']}

install_requires = \
['paramiko>=2.11.0,<3.0.0',
 'requests>=2.28.1,<3.0.0',
 'typer[all]>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['yvpn = yvpn.main:main']}

setup_kwargs = {
    'name': 'yvpn',
    'version': '0.1.0',
    'description': '',
    'long_description': "# Client\n\nThe client is a simple command line tool that can request the creation or destruction of VPN endpoints.\n\nWhen the command is run it should check that wireguard is installed and the user's token is set as an environment variable.  Display helpful error messages if not.\n\n## It consists of the following subcommands:\n\n### `connect`\n\n- Triggers the call to the command and control server to create a new endpoint\n- Optional `location` argument to specify the geographic location where the new endpoint should be created\n- After successful response from the command and control server, automatically initiate key exchange with the endpoint\n- After successful key exchange automatically populate required fields in the returned `wg0.conf` file and store it\n- Activate the wg tunnel\n\n### `disconnect`\n\n- Deactivate the wg connection and tell the command and control server to kill the endpoint\n\n",
    'author': 'Ben Simcox',
    'author_email': 'ben@bnsmcx.com',
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
