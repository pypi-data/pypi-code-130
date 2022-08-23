# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spotdl',
 'spotdl.console',
 'spotdl.download',
 'spotdl.providers',
 'spotdl.providers.audio',
 'spotdl.providers.lyrics',
 'spotdl.types',
 'spotdl.utils']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0',
 'fastapi>=0.78.0,<0.79.0',
 'mutagen>=1.45.1,<2.0.0',
 'nest_asyncio>=1.5.4,<2.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-slugify>=6.1.1,<7.0.0',
 'pytube>=12.1.0,<13.0.0',
 'rapidfuzz>=2.0.15,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'rich>=12.4.4,<13.0.0',
 'spotipy>=2.19.0,<3.0.0',
 'uvicorn>=0.17.1,<0.18.0',
 'yt-dlp>=2022.5.18,<2023.0.0',
 'ytmusicapi>=0.22.0,<0.23.0']

entry_points = \
{'console_scripts': ['spotdl = spotdl:console_entry_point']}

setup_kwargs = {
    'name': 'spotdl',
    'version': '4.0.0rc3',
    'description': 'Download your Spotify playlists and songs along with album art and metadata',
    'long_description': '<!--- mdformat-toc start --slug=github --->\n\n<!--- \n!!! IF EDITING THE README, ENSURE TO COPY THE WHOLE FILE TO index.md in `/docs/`\n--->\n\n<div align="center">\n\n# spotDL v4\n\nDownload your Spotify playlists and songs along with album art and metadata\n\n[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?style=flat-square&color=44CC11)](https://github.com/spotDL/spotify-downloader/blob/master/LICENSE)\n[![PyPI version](https://img.shields.io/pypi/pyversions/spotDL?color=%2344CC11&style=flat-square)](https://pypi.org/project/spotdl/)\n![GitHub commits since latest release (by date)](https://img.shields.io/github/commits-since/spotDL/spotify-downloader/latest?color=44CC11&style=flat-square)\n[![PyPi downloads](https://img.shields.io/pypi/dw/spotDL?label=downloads@pypi&color=344CC11&style=flat-square)](https://pypi.org/project/spotdl/)\n![Contributors](https://img.shields.io/github/contributors/spotDL/spotify-downloader?style=flat-square)\n[![Discord](https://img.shields.io/discord/771628785447337985?label=discord&logo=discord&style=flat-square)](https://discord.gg/xCa23pwJWY)\n\n</div>\n\n> A new and improved version of spotDL: still the fastest, easiest and most accurate command-line music downloader\n\n---\n\n**[Read the documentation on ReadTheDocs!](http://spotdl.rtfd.io/)**\n\n---\n\n## Prerequisites\n\n- [Visual C++ 2019 redistributable](https://docs.microsoft.com/pl-pl/cpp/windows/latest-supported-vc-redist?view=msvc-170#visual-studio-2015-2017-2019-and-2022) **(on Windows)**\n- Python 3.7 or above (added to PATH)\n\n> **_YouTube Music must be available in your country for spotDL to work. This is because we use YouTube Music to filter search results. You can check if YouTube Music is available in your country, by visiting [YouTube Music](https://music.youtube.com)._**\n\n## Installation\n\nRefer to our [Installation Guide](https://spotdl.rtfd.io/en/latest/installation/) for more details\n\n\n- Python (**Recommended**)\n  - _spotDL_ can be installed by running `pip install spotdl`.\n  > On some systems you might have to change `pip` to `pip3`.\n\n### Other options\n\n- Prebuilt Executable\n  - You can download the latest version from the [Releases Tab](https://github.com/spotDL/spotify-downloader/releases)\n- On Termux\n  - `curl -L https://raw.githubusercontent.com/spotDL/spotify-downloader/master/scripts/termux.sh | sh`\n- Arch\n  - There is an Arch User Repository (AUR) package for [spotDL](https://aur.archlinux.org/packages/python-spotdl/).\n- Docker\n  - Build image:\n\n    ```bash\n    docker build -t spotdl .\n    ```\n\n  - Launch container with spotDL parameters (see section below). You need to create mapped volume to access song files\n\n    ```bash\n    docker run --rm -v $(pwd):/music spotdl download [trackUrl]\n    ```\n\n\n### Installing FFmpeg\n\nIf using FFmpeg only for spotDL, you can install FFmpeg to your local directory.  \n`spotdl --download-ffmpeg` will download FFmpeg to your spotDL installation directory.\n\nWe recommend the above option, but if you want to install FFmpeg system-wide,\n\n- [Windows Tutorial](https://windowsloop.com/install-ffmpeg-windows-10/)\n- OSX - `brew install ffmpeg`\n- Linux - `sudo apt install ffmpeg` or use your distro\'s package manager\n\n## Usage\n\nTo get started right away:\n\n```sh\nspotdl download [urls]\n```\n\nTo start the Web UI:\n\n```sh\nspotdl web\n```\n\nYou can run _spotDL_ as a package if running it as a script doesn\'t work:\n\n```sh\npython -m spotdl [urls]\n```\n\n---\n\n### Further information can be found in our documentation\n\n**[Read the documentation on ReadTheDocs!](http://spotdl.rtfd.io/)**\n\n---\n\n## Contributing\n\nInterested in contributing? Check out our [CONTRIBUTING.md](docs/CONTRIBUTING.md) to find\nresources around contributing along with a guide on how to set up a development environment.\n\n## License\n\nThis project is Licensed under the [MIT](/LICENSE) License.\n',
    'author': 'spotDL Team',
    'author_email': 'spotdladmins@googlegroups.com',
    'maintainer': 'xnetcat',
    'maintainer_email': 'xnetcat.dev@gmail.com',
    'url': 'https://github.com/spotDL/spotify-downloader/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
