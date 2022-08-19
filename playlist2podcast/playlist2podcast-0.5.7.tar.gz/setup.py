# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['playlist2podcast']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.0.0,<10.0.0',
 'arrow>=1.2.1,<2.0.0',
 'feedgen>=0.9.0,<0.10.0',
 'outdated>=0.2.1,<0.3.0',
 'requests>=2.28.1,<3.0.0',
 'rich>=12.2.0,<13.0.0',
 'typing-extensions>=4.2.0,<5.0.0',
 'yt-dlp>=2022.1.21,<2023.0.0']

entry_points = \
{'console_scripts': ['playlist2podcast = '
                     'playlist2podcast.playlist_2_podcast:main']}

setup_kwargs = {
    'name': 'playlist2podcast',
    'version': '0.5.7',
    'description': 'Creates podcast feed from playlist URL',
    'long_description': '# Playlist2Podcast\n\n[![Repo](https://img.shields.io/badge/repo-Codeberg.org-blue)](https://codeberg.org/PyYtTools/Playlist2Podcasts)\n[![Downloads](https://pepy.tech/badge/playlist2podcast)](https://pepy.tech/project/playlist2podcast)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Checked against](https://img.shields.io/badge/Checked-Safety--DB-blue)](https://pyup.io/safety/)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/playlist2podcast)\n![PyPI - Wheel](https://img.shields.io/pypi/wheel/playlist2podcast)\n[![CI / Woodpecker](https://ci.codeberg.org/api/badges/PyYtTools/Playlist2Podcasts/status.svg)](https://ci.codeberg.org/PyYtTools/Playlist2Podcasts)\n\n\nPlaylist2Podcast is a command line tool that takes a Youtube playlist and creates a podcast feed from this.\n\n\nPlaylist2Podcast:\n1) downloads and converts the videos in one or more playlists to opus audio only files,\n2) downloads thumbnails and converts them to JPEG format, and\n3) creates a podcast feed with the downloaded videos and thumbnails.\n\nEasiest way to use Playlist2Podcast is to use `pipx` to install it from PyPi. Then you can simply use\n`playlist2podcast` on the command line run it.\n\nPlaylist2Podcast will ask for all necessary parameters when run for the first time and store them in `config.json`\nfile in the current directory.\n\nPlaylist2Podcast is licences under\nthe [GNU Affero General Public License v3.0](http://www.gnu.org/licenses/agpl-3.0.html)\n',
    'author': 'marvin8',
    'author_email': 'marvin8@tuta.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://codeberg.org/PyYtTools/Playlist2Podcasts',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.4,<4.0.0',
}


setup(**setup_kwargs)
