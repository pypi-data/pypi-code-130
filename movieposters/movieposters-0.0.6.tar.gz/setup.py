# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['movieposters']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0', 'lxml>=4.9.1,<5.0.0']

setup_kwargs = {
    'name': 'movieposters',
    'version': '0.0.6',
    'description': "A simple Python package to get the link a movie's poster given its title.",
    'long_description': "## movieposters\n\nA simple Python package to get the link a movie's poster given its title.\n\n## Installation\n\nInstallation has been made easy with PyPI. Depending on your system, you should either run\n\n```pip install movieposters```\n\nor\n\n```pip3 install movieposters```\n\nto install **movieposters**.\n\n## How to use\nSee the example below:\n```python\nimport movieposters as mp\nlink = mp.get_poster(title='breakfast club')\nassert link == mp.get_poster(id='tt0088847')  # can also be found using movie's id\nassert link == mp.get_poster(id=88847)\nassert link == 'https://m.media-amazon.com/images/M/MV5BOTM5N2ZmZTMtNjlmOS00YzlkLTk3YjEtNTU1ZmQ5OTdhODZhXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_UX182_CR0,0,182,268_AL_.jpg'\n```\n\n#### Movies not on IMDb\nIf **movieposters** is *unable* to find the title on IMDb an `mp.errors.MovieNotFound` exception will be raised.\n\n#### Movies without posters\nIf **movieposters** is *able* to find the title on IMDb but can't find its poster an `mp.errors.PosterNotFound` exception will be raised.\n",
    'author': 'Thomas Breydo',
    'author_email': 'tbreydo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/thomasbreydo/movieposters',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
