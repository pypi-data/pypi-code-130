# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nwce']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nwce',
    'version': '0.2.0',
    'description': 'NWCE stands for NetWork Configuration Editor and helps you parsing Cisco configurations',
    'long_description': '[![Python 3.7](https://img.shields.io/badge/python-3.7-green.svg)](https://docs.python.org/3.7/)\n[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)\n\n# nwce\n\n*nwce* is a Python library that can parse Cisco configuration files. I wrote it mainly for Nexus devices but it \nshould work for any indented configuration files.\n\n## Disclaimer\n\nThis library is still in the very early development stages and the API could be broken without notice.\n\n## Getting Started\n\nTests provide a very good starting point before I start writing the documentation.\n\n### Installing\n\n```\npip install nwce\n```\n\n## Running the tests\n\n```\npython -v tests/\n```\n\n## Limitations\n\n## Contributing\n\nPlease read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct.\n\n## Building\n\n```\npoetry build\npoetry publish\n```\n\n## Versioning\n\nWe use [SemVer](http://semver.org/) for versioning. For the versions available, see\nthe [tags on this repository](https://github.com/desnoe/gns3-client/tags).\n\n## Authors\n\n* **Olivier Desnoë** - *Initial work* - [Albatross Networks](http://albatross-networks.com)\n\nSee also the list of [contributors](https://github.com/desnoe/nwce/contributors) who participated in this\nproject.\n\n## License\n\nThis project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details',
    'author': 'DESNOË Olivier (Canal Plus)',
    'author_email': 'olivier.desnoe@canal-plus.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/desnoe/nwce',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
