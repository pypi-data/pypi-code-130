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
    'version': '0.2.0',
    'description': 'Function Cache Management Tool for Python',
    'long_description': '# CacheStore\n\n[![Actions Status](https://github.com/altescy/cachestore/workflows/CI/badge.svg)](https://github.com/altescy/cachestore/actions/workflows/ci.yml)\n[![Python version](https://img.shields.io/pypi/pyversions/cachestore)](https://github.com/altescy/cachestore)\n[![License](https://img.shields.io/github/license/altescy/cachestore)](https://github.com/altescy/cachestore/blob/master/LICENSE)\n[![pypi version](https://img.shields.io/pypi/v/cachestore)](https://pypi.org/project/cachestore/)\n\n**CacheStore** is a simple cache management system for Python functions.\nYou can reuse the cached results even accross different executions.\n\n**cachestore** command enables you to manage the cached results from command line.\nPlease see `--help` for more details.\n\n**Features**\n\n- Caching execution results by decorating target functions easily\n- Exporting caches into an external storage to reuse them access different exeutions\n- Detecting appropreate caches based on argumetns/source code of functions\n- Changing cache behavior via configuration file (see [exmaples](./examples))\n- Providing a useful command line tool to manage caches\n- Written in pure Python, no external dependencies\n\n## Installation\n\n```bash\npip install cachestore\n```\n\n## Usage\n\n### Python\n\n```python\nfrom cachestore import Cache\n\ncache = Cache()\n\n@cache()\ndef awesome_function(x, *, y="y", **kwargs):\n    ...\n```\n\n### CLI\n\n```bash\n$ cachestore --help\nusage: cachestore\n\npositional arguments:\n  {list,prune,remove}\n\noptional arguments:\n  -h, --help           show this help message and exit\n  --version            show program\'s version number and exit\n```\n',
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
