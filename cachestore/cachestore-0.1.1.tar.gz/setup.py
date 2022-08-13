# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cachestore',
 'cachestore.commands',
 'cachestore.common',
 'cachestore.formatters',
 'cachestore.hashers',
 'cachestore.storages']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['cachestore = cachestore.__main__:run']}

setup_kwargs = {
    'name': 'cachestore',
    'version': '0.1.1',
    'description': 'Function Cache Management Tool for Python',
    'long_description': '# CacheStore\n\n[![Actions Status](https://github.com/altescy/cachestore/workflows/CI/badge.svg)](https://github.com/altescy/cachestore/actions/workflows/ci.yml)\n[![Python version](https://img.shields.io/pypi/pyversions/cachestore)](https://github.com/altescy/cachestore)\n[![License](https://img.shields.io/github/license/altescy/cachestore)](https://github.com/altescy/cachestore/blob/master/LICENSE)\n[![pypi version](https://img.shields.io/pypi/v/cachestore)](https://pypi.org/project/cachestore/)\n\nFunction Cache Management Tool for Python\n\n## Installation\n\n```bash\npip install cachestore\n```\n\n## Usage\n\n### Python\n\n```python\nfrom cachestore import Cache\n\ncache = Cache()\n\n@cache()\ndef awesome_function(x, *, y="y", **kwargs):\n    ...\n```\n\n### CLI\n\n```bash\n$ cachestore --help\nusage: cachestore\n\npositional arguments:\n  {list,remove}\n\noptional arguments:\n  -h, --help     show this help message and exit\n  --version      show program\'s version number and exit\n```\n',
    'author': 'altescy',
    'author_email': 'altescy@fastmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/altescy/cachestore',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
