# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['unitunes', 'unitunes.services']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'dearpygui>=1.6.2,<2.0.0',
 'musicbrainzngs>=0.7.1,<0.8.0',
 'pydantic>=1.9.0,<2.0.0',
 'ratelimit>=2.2.1,<3.0.0',
 'spotipy>=2.19.0,<3.0.0',
 'strsimpy>=0.2.1,<0.3.0',
 'tqdm>=4.64.0,<5.0.0',
 'youtube-title-parse>=1.0.0,<2.0.0',
 'ytmusicapi>=0.21.0,<0.22.0']

entry_points = \
{'console_scripts': ['unitunes = gui.main:main']}

setup_kwargs = {
    'name': 'unitunes',
    'version': '2.0.0',
    'description': 'A GUI and library to manage playlists across music streaming services.',
    'long_description': '# unitunes [![PyPI version](https://badge.fury.io/py/unitunes.svg)](https://badge.fury.io/py/unitunes) ![example workflow](https://github.com/platers/unitunes/actions/workflows/github-actions.yml/badge.svg)\n\n![unituneslogo](assets/unitunes.png)\n\nA python GUI and library to sync playlists across music streaming services.\n\n![playlist_tab](assets/playlist_tab.png)\n\n## Introduction\n\nunitunes manages playlists across streaming services. unitunes can transfer songs between services and keep playlists in sync.\n\nunitunes stores your playlists in plain text, allowing you to version control your music. Playlists can be pushed and pulled from streaming services. Tracks from one service can be searched on another.\n\n### Current Supported Streaming Services\n\n| Name          | Pullable | Pushable | Searchable |\n| ------------- | :------: | :------: | :--------: |\n| MusicBrainz   |          |          |     ✅     |\n| Spotify       |    ✅    |    ✅    |     ✅     |\n| Youtube Music |    ✅    |    ✅    |     ✅     |\n| Beatsaber     |    ✅    |    ✅    |     ✅     |\n\nWant to add support for another service? See [contributing](#contributing).\n\n## Usage\n\n```bash\npip install unitunes\nunitunes\n```\n\nIn settings, set the directory to store your playlists. You can version control this directory with git.\n\nConnect services in the service tab. Enter a service name, and click the button to add the corresponding service. Each service type requires some configuration, Spotify requires a client id and secret, and Youtube Music requires request headers.\n![service_tab](assets/service_tab.png)\n\nPlaylists can then be added to the playlist tab.\n\nAfter adding playlists, you can sync them. You likely just want to press the `Sync All` button, which will pull, search, and push all playlists.\n\n## Contributing\n\nunitunes is rapidly evolving. Take a look at the [contributing guide](CONTRIBUTING.md).\n',
    'author': 'platers',
    'author_email': 'platers81@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/platers/unitunes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
