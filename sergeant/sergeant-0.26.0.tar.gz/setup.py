# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sergeant',
 'sergeant.connector',
 'sergeant.encoder',
 'sergeant.encoder.compressor',
 'sergeant.encoder.serializer',
 'sergeant.executor',
 'sergeant.killer',
 'sergeant.logging']

package_data = \
{'': ['*']}

install_requires = \
['hiredis>=2,<3',
 'msgpack>=1,<2',
 'orjson>=3,<4',
 'psutil>=5,<6',
 'pymongo>=3.0,<5.0',
 'redis>=4,<5',
 'typing_extensions>=3.10,<4.0']

setup_kwargs = {
    'name': 'sergeant',
    'version': '0.26.0',
    'description': 'Fast, Safe & Simple Asynchronous Task Queues Written In Pure Python',
    'long_description': '<p align="center">\n    <a href="https://github.com/intsights/sergeant">\n        <img src="https://raw.githubusercontent.com/intsights/sergeant/master/images/logo.png" alt="Logo">\n    </a>\n    <h3 align="center">\n        Fast, Safe & Simple Asynchronous Task Queues Written In Pure Python\n    </h3>\n</p>\n\n![license](https://img.shields.io/badge/MIT-License-blue)\n![Python](https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)\n![Build](https://github.com/intsights/sergeant/workflows/Build/badge.svg)\n[![PyPi](https://img.shields.io/pypi/v/sergeant.svg)](https://pypi.org/project/sergeant/)\n\n## Table of Contents\n\n- [Table of Contents](#table-of-contents)\n- [About The Project](#about-the-project)\n  - [Built With](#built-with)\n  - [Performance](#performance)\n  - [Installation](#installation)\n- [Documentation](#documentation)\n- [Usage](#usage)\n- [License](#license)\n- [Contact](#contact)\n\n\n## About The Project\n\n`Sergeant` is a comprehensive distributed workers framework. The library was written in [Intsights](https://intsights.com/) after failing to use `celery` with high scale. The library focuses on process and thread safety (through process/thread killers), performance and ease of use.\n\n\n### Built With\n\n* [orjson](https://github.com/ijl/orjson)\n* [msgpack](https://github.com/msgpack/msgpack-python)\n* [pymongo](https://github.com/mongodb/mongo-python-driver)\n* [redis](https://github.com/andymccurdy/redis-py)\n* [psutil](https://github.com/giampaolo/psutil)\n\n\n### Performance\n\nBenchmark code can be found inside `benchmark` directory.\n\n\n### Installation\n\n```sh\npip3 install sergeant\n```\n\n\n## Documentation\n\nMore information can be found on the [documentation](https://intsights.github.io/sergeant/) site.\n\n## Usage\n\nUsage examples can be found inside `examples` directory.\n\n\n## License\n\nDistributed under the MIT License. See `LICENSE` for more information.\n\n\n## Contact\n\nGal Ben David - gal@intsights.com\n\nProject Link: [https://github.com/intsights/sergeant](https://github.com/intsights/sergeant)\n',
    'author': 'Gal Ben David',
    'author_email': 'gal@intsights.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Intsights/sergeant',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
