# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['click_params']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<9.0', 'validators>=0.18,<0.19']

setup_kwargs = {
    'name': 'click-params',
    'version': '0.4.0',
    'description': 'A bunch of useful click parameter types',
    'long_description': '# click-params\n\n[![Pypi version](https://img.shields.io/pypi/v/click-params.svg)](https://pypi.org/project/click-params/)\n![](https://github.com/click-contrib/click_params/workflows/CI/badge.svg)\n[![Coverage Status](https://codecov.io/gh/click-contrib/click_params/branch/master/graphs/badge.svg?branch=master)](https://codecov.io/gh/click-contrib/click_params)\n[![Documentation Status](https://readthedocs.org/projects/click_params/badge/?version=latest)](https://click-params.readthedocs.io/en/latest/?badge=latest)\n[![License Apache 2](https://img.shields.io/hexpm/l/plug.svg)](http://www.apache.org/licenses/LICENSE-2.0)\n[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/click-contrib/click_params)\n\nA bunch of useful click parameter types.\n\n## Why?\n\nI often find myself wanting to use a click parameter able to handle list of strings, so I decide to put this in a library\nand I ended adding more parameter types that can be useful for various scripts including network, mathematics and so on.\n\n\n## Installation\n\n```bash\npip install click-params\n```\n\nclick-params starts working from **python 3.7**. It has a few dependencies:\n- [click](https://click.palletsprojects.com/en/7.x/) >= 7.0\n- [validators](https://validators.readthedocs.io/en/latest/)\n\n## Usage\n\n```python\nimport click\nfrom click_params import Ipv4AddressListParamType\n\n@click.command()\n@click.option(\'-a\', \'--addresses\', help=\'list of ipv4 addresses\', prompt=\'list of ipv4 addresses to reserve\',\n type=Ipv4AddressListParamType())\ndef pool(addresses):\n    click.echo(\'reserved ips:\')\n    for ip in addresses:\n        click.echo(ip)\n```\n\n```bash\n$ pool --addresses=\'192.168.1.1,192.168.1.14\'\nreserved ips:\n192.168.1.1\n192.168.1.14\n```\n\nYou can change the default separator "," by passing it when initializing the parameter type.\n\n## Documentation\n\nDocumentation is available at https://click-params.readthedocs.io/en/latest/.\n',
    'author': 'lewoudar',
    'author_email': 'lewoudar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://click-params.readthedocs.io/en/stable',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
