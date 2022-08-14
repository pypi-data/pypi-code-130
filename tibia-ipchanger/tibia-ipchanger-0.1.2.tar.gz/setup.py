# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ipchanger']

package_data = \
{'': ['*']}

install_requires = \
['pyelftools>=0.28,<0.29']

entry_points = \
{'console_scripts': ['ipchanger = ipchanger:run']}

setup_kwargs = {
    'name': 'tibia-ipchanger',
    'version': '0.1.2',
    'description': 'Command-line IP changer for Tibia clients (Linux only)',
    'long_description': 'tibia-ipchanger\n===============\n\nInstalling\n----------\n\nInstall from [PyPI](https://pypi.org/project/tibia-ipchanger/) using `pip`:\n\n```\n$ pip install --upgrade tibia-ipchanger\n```\n\nOr, even better, install with [`pipx`](https://pypi.org/project/pipx/):\n\n```\n$ pipx install tibia-ipchanger\n```\n\nUsage\n-----\n\nRun `ipchanger <basedir>`, where `basedir` is the path to the directory where the\nlauncher is installed. This is the directory containing an executable named `Tibia`, a\nfile named `launchermetadata.json` and a directory named `packages`.\n\nIt is **NOT** the directory containing `3rdpartylicenses` `assets`, `bin` and other\nclient data, but two directories parent to that one.\n\nTo replace an URL, simply pass `--url-as-snake-case <new url>` to the command line,\ne.g. `ipchanger path/to/Tibia --login-web-service https://myot.com/login.php` will\nreplace `loginWebService` with `https://myot.com/login.php`.\n\nThe script will create a temporary version of your currently installed client that is\nrestored after immediately launch, so you can still play regular Tibia by launching the\nclient as usual.\n\nTo see a list of available URLs to change, run `ipchanger -h`:\n\n```\n$ ipchanger -h\n...\n  --tibia-page-url TIBIA_PAGE_URL\n  --tibia-store-get-coins-url TIBIA_STORE_GET_COINS_URL\n  --get-premium-url GET_PREMIUM_URL\n  --create-account-url CREATE_ACCOUNT_URL\n  --create-tournament-character-url CREATE_TOURNAMENT_CHARACTER_URL\n  --access-account-url ACCESS_ACCOUNT_URL\n  --lost-account-url LOST_ACCOUNT_URL\n  --manual-url MANUAL_URL\n  --faq-url FAQ_URL\n  --premium-features-url PREMIUM_FEATURES_URL\n  --limesurvey-url LIMESURVEY_URL\n  --hints-url HINTS_URL\n  --twitch-tibia-url TWITCH_TIBIA_URL\n  --youtube-tibia-url YOUTUBE_TIBIA_URL\n  --crash-report-url CRASH_REPORT_URL\n  --fps-history-recipient FPS_HISTORY_RECIPIENT\n  --tutorial-progress-web-service TUTORIAL_PROGRESS_WEB_SERVICE\n  --tournament-details-url TOURNAMENT_DETAILS_URL\n  --login-web-service LOGIN_WEB_SERVICE\n  --client-web-service CLIENT_WEB_SERVICE\n```\n\nURLs that are not set will be kept as original. The total length of replaced URLs must\nnot exceed the total length of the original URLs that are to be replaced, in which case\nthe script will fail to launch the client.\n\nLicense\n-------\n\nWork licensed under the [MIT License](LICENSE).\n',
    'author': 'Ranieri Althoff',
    'author_email': 'ranisalt@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ranisalt/tibia-ipchanger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
