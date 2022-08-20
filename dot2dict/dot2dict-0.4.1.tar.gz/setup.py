# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dot2dict']

package_data = \
{'': ['*']}

install_requires = \
['rich>=12.5.1,<13.0.0', 'typer[all]>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['dot2dict = dot2dict.dot2dict_typer:start']}

setup_kwargs = {
    'name': 'dot2dict',
    'version': '0.4.1',
    'description': 'JSON dot notation to Python Dictionary 🐍 / Ruby Hash ♦️ Notation Converter',
    'long_description': '# dot2dict - JSON dot notation to Python Dictionary 🐍 / Ruby Hash ♦️ Notation Converter\n\n\nVersion : 0.4.1 Alpha\n\nThe Package is still under development and considered unstable for use.\nPlease feel free to use it and report bugs.\n\n## Installation:\n\ndot2dict is available in Python Package Index.\nInstall with pip with your favourite python distribution.\n\n```shell\npip3 install dot2dict\n```\n\nInstall and get started right away.\n\n## Features\n\n* Convert JSON dot notation path to Python Dictionary path.\n* Convert JSON dot notation path to Ruby Hash path.\n* Rich Formatting\n* Sensible Defaults.\n* Beautiful Output.\n* Free and open.\n\n\n## Screenshots\n\n![Example 1](https://github.com/insumanth/file_assets/blob/main/dot2dict/screenshot_01.png?raw=true)\n\n## Development\n\nCurrently in Alpha. \n\n![alt text](https://github.com/insumanth/file_assets/blob/main/dot2dict/timeline.png?raw=true)\n\n\n## To-Do\n\n - [x] Alpha Release\n - [ ] Add Documentation.\n - [ ] Convert Python f-strings to String format to support older python versions.\n - [ ] Fix ambiguous flags.\n - [ ] Beta Release\n - [ ] Adding Support for Other languages other than Python and Ruby.\n\n\n\n',
    'author': 'Sumanth',
    'author_email': 'sumanthreddystar@gmail.com',
    'maintainer': 'Sumanth',
    'maintainer_email': 'sumanthreddystar@gmail.com',
    'url': 'https://pypi.org/project/dot2dict/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
