# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['wrapper']

package_data = \
{'': ['*']}

install_requires = \
['kraken-core>=0.8.6,<0.9.0',
 'pex>=2.1.103,<3.0.0',
 'setuptools>=33.0.0',
 'tomli>=2.0.1,<3.0.0',
 'tomli_w>=1.0.0,<2.0.0']

entry_points = \
{'console_scripts': ['krakenw = kraken.wrapper.main:main']}

setup_kwargs = {
    'name': 'kraken-wrapper',
    'version': '0.1.13',
    'description': '',
    'long_description': '# kraken-wrapper\n\nProvides the `krakenw` command which is a wrapper around Kraken to construct an isolated and reproducible build\nenvironment.\n\n__Features__\n\n* Produces isolated environments in PEX format\n* Reads build requirements from the `.kraken.py` file header\n* Produces lock files (`.kraken.lock`) that can be used to reconstruct an exact build environment <sup>1)</sup>\n\n<sup>1) The lock files do not contain hashes for installed distributions, but only the exact version numbers from\nthe resolved build environment.</sup>\n\n__Requirements header__\n\nIf no `.kraken.lock` file is present, Kraken wrapper will read the header of the `.kraken.py` file to obtain the\nrequirements to install into the build environment. The format of this header is demonstrated below:\n\n```py\n# ::requirements kraken-std>=0.3.0,<0.4.0 --extra-index-url https://...\n# ::pythonpath build-support\n```\n\nThe available options are:\n\n* **`requirements`**: Here you can specify any number of Pip requirements or local requirements (of the\n    format `dist-name @ path/to/dist`) as well as `--index-url`, `--extra-index-url` and `--interpreter-constraint`.\n* **`pythonpath`**: One or more paths to add the `sys.path` before your build script is executed. The `build-script` folder\n    is always added by default (as is the default behaviour by the `kraken-core` Python script project loader).\n\n__Environment variables__\n\n* `KRAKENW_USE`: If set, it will behave as if the `--use` flag was specified (although the `--use` flag if given\n    will still take precedence over the environment variable). Can be used to enforce a certain type of build\n    environment to use (available values are `PEX_ZIPAPP` (default), `PEX_PACKED`, `PEX_LOOSE` and `VENV`).\n* `KRAKENW_REINSTALL`: If set to `1`, behaves as if `--reinstall` was specified.\n* `KRAKENW_INCREMENTAL`: If set to `1`, virtual environment build environments are "incremental", i.e. they will\n    be reused if they already exist and their installed distributions will be upgraded.\n\n__Recommendations__\n\nWhen using local requirements, using the `VENV` type is a lot fast because it can leverage Pip\'s `in-tree-build`\nfeature. Pex [does not currently support in-tree builds](https://github.com/pantsbuild/pex/issues/1357#issuecomment-860133766).\n',
    'author': 'Unknown',
    'author_email': 'me@unknown.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
