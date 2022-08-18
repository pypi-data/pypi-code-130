# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spotifetch']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'colorgram.py>=1.2.0,<2.0.0',
 'kolorz>=0.2.1,<0.3.0',
 'requests>=2.27.1,<3.0.0',
 'spotipy>=2.19.0,<3.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['spotifetch = spotifetch.cli:main']}

setup_kwargs = {
    'name': 'spotifetch',
    'version': '0.4.1',
    'description': 'A fetch tool for Spotify',
    'long_description': '<h2 align="center"> ━━━━━━  ❖  ━━━━━━ </h2>\n\n<!-- BADGES -->\n<div align="center">\n   <p></p>\n   \n   <img src="https://img.shields.io/github/stars/dotzenith/SpotiFetch?color=F8BD96&labelColor=302D41&style=for-the-badge">   \n\n   <img src="https://img.shields.io/github/forks/dotzenith/SpotiFetch?color=DDB6F2&labelColor=302D41&style=for-the-badge">   \n\n   <img src="https://img.shields.io/github/repo-size/dotzenith/SpotiFetch?color=ABE9B3&labelColor=302D41&style=for-the-badge">\n   \n   <img src="https://img.shields.io/github/commit-activity/y/dotzenith/SpotiFetch?color=96CDFB&labelColor=302D41&style=for-the-badge&label=COMMITS"/>\n   <br>\n</div>\n\n<p/>\n\n---\n\n### ❖ Information \n\n  SpotiFetch is a simple fetch tool to display info about your Spotify profile using the spotify API\n\n  <img src="https://github.com/dotzenith/dotzenith/blob/main/assets/SpotiFetch/spotifetch.gif" alt="spotifetch gif">\n\n---\n\n### ❖ Requirements\n\nRegister an app on the Spotify developer dashboard [here](https://developer.spotify.com/dashboard/)\n\nEdit the app settings and set `http://127.0.0.1:9090` as the redirect URI\n\nTake a note of your Client ID and Client Secret\n\nPut the following in your `.bashrc` or `.zshrc` or the equivalent for your shell\n```sh\nexport SPOTIPY_CLIENT_ID=\'insert-your-spotify-client-id-here\'\nexport SPOTIPY_CLIENT_SECRET=\'insert-your-spotify-client-secret-here\'\nexport SPOTIPY_REDIRECT_URI=\'http://127.0.0.1:9090\'\n```\n\n---\n\n### ❖ Installation\n\n> Install from pip\n```sh\n$ pip3 install spotifetch\n```\n\n> Install from source\n- First, install [poetry](https://python-poetry.org/)\n```sh\n$ git clone https://github.com/ZenithDS/SpotiFetch.git\n$ cd SpotiFetch\n$ poetry build\n$ pip3 install ./dist/SpotiFetch-0.4.1.tar.gz\n```\n\n\n### ❖ Usage \n\nIf the instructions in the Requirements section are followed properly, SpotiFetch will ask you to log in and give permissions to fetch stats the first time it\'s used. Login is not required after the first use. \n\n```\nUsage: spotifetch [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  profile      Fetch stats for the user profile\n  top-artists  Fetch user\'s top artists\n  top-tracks   Fetch user\'s top tracks\n```\n\n\n#### SpotiFetch can be used like any other fetch tool\n\n```sh\n$ spotifetch profile      # fetches profile stats\n$ spotifetch top-artists  # fetches your top five artists\n$ spotifetch top-tracks   # fetches your top five songs\n```\n\n\n#### The top artists and tracks depends on the time-frame. By default, SpotiFetch fetches your top artists in the short term, but mid term, and long term are also available using the `--term`/`-t` option.\n\n```sh\n$ spotifetch top-artists -t short # fetches top artists in the short term\n$ spotifetch top-artists -t mid   # fetches top artists in the mid term\n$ spotifetch top-artists -t long  # fetches top artists in the long term\n```\n\n> The `--term`/`-t` option is available for all three of the commands \n\n\n#### SpotiFetch supports `--no-random`/`-n` option to print the spotify ascii art with a green outline instead of a using a random color from the colorscheme\n\n```sh\n$ spotifetch profile      # prints spotify art with random color\n$ spotifetch profile -n   # prints green spotify art\n```\n\n> The `--random`/`-r` option is also available for all three of the commands\n\n\n#### The `--all-artists`/`-a` option can be used to display all artists on a track instead of just displaying one\n\n```sh\n$ spotifetch profile                 # Displays only one artist for a track \n$ spotifetch profile --all-artists   # Displays all artists for a track\n```\n\n> The `--all-artists`/`-a` option is available for the `profile` and `top-tracks` commands\n\n\n#### SpotiFetch can be used with a variety of different color schemes.\n\n> SpotiFetch uses [catppuccin](https://github.com/catppuccin) as it\'s default color scheme, but a different one can be specified using the `--color`/`-c` option. \n\nFor example:\n```sh\n$ spotifetch profile         # uses catppuccin\n$ spotifetch profile -c nord # uses nord \n```\n\n> The `--color`/`-c` option is available for all three of the commands\n\nSupported color schemes as of now: \n- [catppuccin](https://github.com/catppuccin) - latte, frappe, macchiato, mocha\n- [nord](https://github.com/arcticicestudio/nord)\n- [dracula](https://github.com/dracula/dracula-theme)\n- [gruvbox](https://github.com/morhetz/gruvbox)\n- [onedark](https://github.com/joshdick/onedark.vim)\n- [tokyonight](https://github.com/folke/tokyonight.nvim)\n- [ayu](https://github.com/ayu-theme)\n- [palenight](https://github.com/drewtempelmeyer/palenight.vim)\n- [gogh](https://github.com/Mayccoll/Gogh)\n\n\n#### If you\'re a pywal user, the `--pywal` option can be used to match the SpotiFetch color scheme with the one generated by pywal\n\n```sh\n$ spotifetch profile --pywal   # Uses color scheme generated by pywal\n```\n\n> The `--pywal` option is available for all three of the commands\n\n> NOTE: In order to use the `--pywal` option, the `colors.json` file must be present in `$HOME/.cache/wal/` (`colors.json` is generated automatically when pywal is used)\n\n\n#### SpotiFetch also supports dynamically generated colorschemes using the `--art` option\n\n```sh\n$ spotifetch profile --art      # Generates colorscheme based on the cover art of the recently played song\n$ spotifetch top-artists --art  # Generates colorscheme based on the profile image of the top artist\n$ spotifetch top-tracks --art   # Generates colorscheme based on the cover art of the top track \n```\n\n> If SpotiFetch can\'t generate a colorscheme for any reason, it will fallback to the colorscheme passed in as an option, or the default colorscheme of catppuccin \n\n---\n\n### ❖ About SpotiFetch\n\nSpotiFetch is the direct result of browsing too many unix subreddits and general interest in cli tools. The ascii art for spotify is a WIP and contributions to the logo are welcomed and encouraged! \n\n---\n\n### ❖ What\'s New? \n0.4.1 - Added type hints and switched to kolorz\n\n---\n\n<div align="center">\n\n   <img src="https://img.shields.io/static/v1.svg?label=License&message=MIT&color=F5E0DC&labelColor=302D41&style=for-the-badge">\n\n</div>\n\n',
    'author': 'ZenithDS',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
