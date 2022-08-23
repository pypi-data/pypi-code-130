# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['reddit_gen']

package_data = \
{'': ['*']}

install_requires = \
['2captcha-python>=1.1.0',
 'beautifulsoup4>=4.10.0',
 'factory-boy>=3.2.0',
 'loguru>=0.6.0',
 'pymongo[srv]>=4.1.1',
 'python-dotenv>=0.17.1',
 'requests>=2.26.0',
 'rich>=10.6.0',
 'selenium>=3.141.0',
 'tqdm>=4.56.2']

entry_points = \
{'console_scripts': ['reddit-gen = reddit_gen:cli.main',
                     'reddit_gen = reddit_gen:cli.main']}

setup_kwargs = {
    'name': 'reddit-gen',
    'version': '0.1.2',
    'description': 'Generate Reddit Accounts Automatically',
    'long_description': "# Reddit Account Generator\n\n\n## Requirements\n- [Google Chrome](https://www.google.com/chrome/)\n- [Chrome Driver](https://chromedriver.chromium.org/downloads)\n- *Optional, but recommended:* [MongoDB](https://www.mongodb.com/) (get a free database [here](https://www.mongodb.com/cloud/atlas/register)) \n\n## Getting started\n\n### Step 1: Install the package\n```sh\npip install -U reddit-gen\n```\n\n### Step 2: Configure your environment\n```sh\nreddit-gen --configure\n```\n\n## Usage\n\n```\nusage: reddit-gen [-h] [-d] [-s] [-i] [-j] [-p] [-n CREATE_N_ACCOUNTS]\n                  [-c CONFIG_FILE] [-D] [-U] [--configure]\n                  [--experimental-use-vpn]\n                  [--check-subreddit-ban CHECK_SUBREDDIT_BAN] [-v]\n\noptions:\n  -h, --help            show this help message and exit\n  -d, --disable-headless\n                        Disable headless mode\n  -s, --solve-manually  Solve the captcha manually\n  -i, --ip-rotated      The public IP address was changed by the user since\n                        the last created account (to bypass the cooldown)\n  -j, --use-json        Read from the local JSON database (pass if you're not\n                        using MongoDB). A new local database will be created\n                        if not found\n  -p, --show-local-database-path\n                        Prints the path to the local database, if exists\n  -n CREATE_N_ACCOUNTS, --create-n-accounts CREATE_N_ACCOUNTS\n                        Number of accounts to create (default: 1)\n  -c CONFIG_FILE, --config-file CONFIG_FILE\n                        Path to the config file. Defaults to\n                        /Users/$USER/.redditgen.env\n  -D, --debug           Debug mode\n  -U, --update-database\n                        Update accounts metadata (MongoDB-only)\n  --configure           Configure your environment\n  --experimental-use-vpn\n                        Experimental feature (unstable)\n  --check-subreddit-ban CHECK_SUBREDDIT_BAN\n                        Check if your accounts are banned from a specific\n                        subreddit (MongoDB-only)\n  -v, --verbose         Print more logs\n```\n\n## Example\n\n```sh\n$ reddit-gen\n# ───────────────────────────────── Starting... ─────────────────────────────────\n# 2022-06-20 17:22:42.739 | INFO     | reddit_gen.generator:_signup_info:65 - Your account\\'s email address: some_random_username@example.com\n# 2022-06-20 17:22:42.739 | INFO     | reddit_gen.generator:_signup_info:67 - Username: some_random_username\n# 2022-06-20 17:22:45.976 | DEBUG    | reddit_gen.generator:generate:196 - Solving captcha...\n# 2022-06-20 17:24:12.579 | DEBUG    | reddit_gen.generator:generate:200 - Solved!\n# 2022-06-20 17:24:38.841 | DEBUG    | reddit_gen.generator:generate:263 - Checking account info...\n# 2022-06-20 17:24:39.069 | DEBUG    | reddit_gen.generator:generate:266 - Passed!\n# 2022-06-20 17:24:39.069 | INFO     | reddit_gen.generato──r:generate:274 - Account verified!\n# ───────────────────────────────────── Done! ───────────────────────────────────\n```\n",
    'author': 'Mohammad Alyetama',
    'author_email': 'malyetama@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
