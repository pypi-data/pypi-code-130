# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['redditsfinder']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0', 'rich>=12.5.1,<13.0.0']

entry_points = \
{'console_scripts': ['redditsfinder = redditsfinder:main']}

setup_kwargs = {
    'name': 'redditsfinder',
    'version': '2.1.2',
    'description': "Archive a reddit user's post history. Formatted overview of a profile, JSON containing every post, and picture downloads.",
    'long_description': "# redditsfinder - reddit user info\n\nIt's in a good state again with some quality of life improvements. \n\n**`pip3 install redditsfinder`**\n\n**A program to get reddit user post data.**\n\n```\nRunning redditsfinder\n---------------------\n    Test it on yourself to make sure it works.\n        redditsfinder someusername\n\n    Basic usage\n        redditsfinder username\n        redditsfinder [options] username_0 username_1 username_2 ...\n\n    With an input file\n        -f or --file.\n        redditsfinder [options] -f line_separated_text_file.txt\n\n    Examples\n        - just print the summary table to stdout\n            $ redditsfinder someusername\n\n        - save data locally and print the summary table to stdout\n            $ redditsfinder --write someusername\n\n        - just save data locally without printing\n            $ redditsfinder --write --quiet someusername\n\n        - download pictures\n            $ redditsfinder -pd someusername\n\n    Optional args\n        --pics returns URLs of image uploads\n        -pd or --pics --download downloads them\n            -quiet or -q turns off printing\n\n```\n\n# Demo\n\n## Downloading Images\n\n`redditsfinder -pd someusername`\n\n![download](./imgs/pics_downloader.png)\n\n## Creating a command \n\n`redditsfinder someusername`\n\n![table](./imgs/table.png)\n\n",
    'author': 'fitzy1293',
    'author_email': 'berkshiremind@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Fitzy1293/redditsfinder',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
