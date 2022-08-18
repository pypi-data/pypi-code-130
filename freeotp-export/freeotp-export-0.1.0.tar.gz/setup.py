# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['freeotp_export']

package_data = \
{'': ['*']}

install_requires = \
['qrcode>=7.3.1,<8.0.0']

entry_points = \
{'console_scripts': ['freeotp-export = freeotp_export:main']}

setup_kwargs = {
    'name': 'freeotp-export',
    'version': '0.1.0',
    'description': 'Parse a FreeOTP xml file and present QR codes or strings for import elsewhere',
    'long_description': '# FreeOTP-Export\n[![PyPi Version](https://img.shields.io/pypi/v/freeotp-export.svg)](https://pypi.org/project/freeotp-export/)\n\nRescue your OTP tokens from FreeOTP\n\n## Installing\nYou can install directly through pip: `pip install freeotp-export`\n\nAlternatively, to install from source, clone the repo or download and unpack a\ntarball, then...\n\n- If you already have [poetry](https://python-poetry.org/) installed, you can\n  just run:\n  ```sh\n  $ poetry run freeotp-export tokens.xml\n  ```\n- Otherwise, use pip: `pip install --upgrade .`\n- If you must, running `__main__.py` may work if you have the dependencies\n  installed.\n\n\n## Usage\n### Acquire the File\nIf your phone is rooted, you can just grab the file from\n`/data/data/org.fedorahosted.freeotp/shared_prefs/tokens.xml`\n\nOtherwise, start by enabling debugging on the phone and setting up the android\nplatform tools. Grab a backup off the app data by running\n`adb backup org.fedorahosted.freeotp`, and when asked for a password, don\'t\nenter one.\n\nTo read the resulting Android backup file, `backup.ab`, you can either use\n[android-backup-extractor](https://github.com/nelenkov/android-backup-extractor):\n```sh\n$ abe unpack backup.ab - | tar xv --strip-components=3\n```\n\nOr yolo it by adding the tar header yourself:\n```sh\n$ ( printf "\\x1f\\x8b\\x08\\x00\\x00\\x00\\x00\\x00" ; tail -c +25 backup.ab ) | tar zxv --strip-components=3\n```\n\nYou should then have the token file, `tokens.xml`.\n\n### Read the File\nJust run this tool, and it\'ll give you both the OTP URIs (`otpauth://...`) and\nscannable QR codes. Note that Google Authenticator ignores the `digits`\nparameter, so it does not work for issuers like Blizzard that use lengths other\nthan 6.\n\nIf you used `pip install`: `$ freeotp-export tokens.xml`\n\nOr with Poetry: `$ poetry run freeotp-export tokens.xml`\n\nAfter importing everything to a new app, be sure to delete `tokens.xml` and\n`backup.ab`, since they contain all of your tokens!\n',
    'author': 'Trevor Bergeron',
    'author_email': 'mal@sec.gd',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
