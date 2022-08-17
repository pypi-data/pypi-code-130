# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['th2_act', 'th2_act.util']

package_data = \
{'': ['*']}

install_requires = \
['th2-common>=3.9.1,<4.0.0', 'th2-grpc-check1==3.6.0.dev2433840021']

setup_kwargs = {
    'name': 'th2-act',
    'version': '1.0.0.dev2873917814',
    'description': 'Python library with useful tools for creating custom Act implementations',
    'long_description': '# TH2 Act Component (Python)\n\n## Overview\nThis repository is a library for custom gRPC act projects (check [th2-act-template-py](https://github.com/th2-net/th2-act-template-py) \nfor the implementation template). Check the [Wiki](https://github.com/th2-net/th2-act-py/wiki) for instructions and examples.\n\nThe th2-act contains helper methods to create custom \nActHadlers that implements custom gRPC API. Multiple ActHandlers allowed as well.\n\n## Installation\nTo install `th2-act` package run the following command in the terminal:\n```\npip install th2-act\n```\n',
    'author': 'TH2-devs',
    'author_email': 'th2-devs@exactprosystems.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/th2-net/th2-act-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
