# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pic_resizer']

package_data = \
{'': ['*'], 'pic_resizer': ['static/*', 'templates/*']}

install_requires = \
['Flask>=2.2.1,<3.0.0', 'Pillow>=9.2.0,<10.0.0', 'click>=8.1.3,<9.0.0']

entry_points = \
{'console_scripts': ['pic_resizer = pic_resizer.entry:main']}

setup_kwargs = {
    'name': 'pic-resizer',
    'version': '0.1.8',
    'description': 'A image resizing tool.',
    'long_description': '# pic_resizer\n\nA image resizing tool.\n\n[![PyPI version](https://badge.fury.io/py/pic-resizer.svg)](https://badge.fury.io/py/pic-resizer)\n\n\n## Installation\n\n```bash\npip install pic_resizer\n```\n\n## Usage\n\n```console\n~ ➜ pic_resizer --help\nUsage: pic_resizer [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --version  Show the version and exit.\n  --help     Show this message and exit.\n\nCommands:\n  cli  Operating from the command line\n  web  Operating in the web app\n```\n\n### cli\n\n[![asciicast](https://asciinema.org/a/d5G7DaIrDN048rrLGr1TbJDh1.svg)](https://asciinema.org/a/d5G7DaIrDN048rrLGr1TbJDh1)\n\n### web\n\n![](https://s3.bmp.ovh/imgs/2022/08/09/1d0c289413d7078e.png)\n',
    'author': 'fffzlfk',
    'author_email': '1319933925qq@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fffzlfk/pic_resizer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
