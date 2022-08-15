# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bgetcli']

package_data = \
{'': ['*']}

install_requires = \
['bgetlib>=3.2.7', 'toml>=0.10.2']

entry_points = \
{'console_scripts': ['bget = bgetcli.bget:main']}

setup_kwargs = {
    'name': 'bget',
    'version': '10.0.0',
    'description': 'bget - a python bilibili favourites batch downloader',
    'long_description': '# bget\nbget - a python bilibili favourites batch downloader\n\n## Install\n```bash\npip install bget\n```\n\n## Use\n 1. Download [config.toml](https://github.com/baobao1270/bget/blob/master/config-example.toml) and edit it as your need.\n 2. Get your bilibili.com cookies. You can use [this chrome extension (Get cookies.txt)](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid).\n 3. Download FFMpeg and ensure is in your `PATH`.\n 4. Use `bget -h` to get help.\n\n## Build & Development\nPoetry is used to build and develop.\n\n## License\nMIT License\n',
    'author': 'Joseph Chris',
    'author_email': 'joseph@josephcz.xyz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/baobao1270/bget',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
