# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['wrapper']

package_data = \
{'': ['*']}

install_requires = \
['keyring>=23.8.2,<24.0.0',
 'kraken-core>=0.9.0,<0.10.0',
 'pex>=2.1.103,<3.0.0',
 'setuptools>=33.0.0',
 'termcolor>=1.1.0,<2.0.0',
 'tomli>=2.0.1,<3.0.0',
 'tomli_w>=1.0.0,<2.0.0']

entry_points = \
{'console_scripts': ['krakenw = kraken.wrapper.main:main']}

setup_kwargs = {
    'name': 'kraken-wrapper',
    'version': '0.1.21',
    'description': '',
    'long_description': '# kraken-wrapper\n\nProvides the `krakenw` command which is a wrapper around Kraken to construct an isolated and reproducible build\nenvironment.\n\n### Features\n\n* Produces isolated environments in PEX format\n* Reads build requirements from the `.kraken.py` file header\n* Produces lock files (`.kraken.lock`) that can be used to reconstruct an exact build environment <sup>1)</sup>\n* Store Python package index credentials in a keychain\n\n<sup>1) The lock files do not contain hashes for installed distributions, but only the exact version numbers from\nthe resolved build environment.</sup>\n\n## Documentation\n\n__Table of Contents__\n\n* [Requirements header](#requirements-header)\n* [Environment variables](#environment-variables)\n* [Recommendations](#recommendations)\n* [Index credentials](#index-credentials)\n\n### Requirements header\n\nIf no `.kraken.lock` file is present, Kraken wrapper will read the header of the `.kraken.py` file to obtain the\nrequirements to install into the build environment. The format of this header is demonstrated below:\n\n```py\n# ::requirements kraken-std>=0.3.0,<0.4.0 --extra-index-url https://...\n# ::pythonpath build-support\n```\n\nThe available options are:\n\n| Option | Description |\n| ------ | ----------- |\n| `#::requirements` | The content on this line will be parsed similar to the arguments for `pip install`. Every positional argument is a Python requirement specifier. The following options are supported: `--index-url`, `--extra-index-url` and `--interpreter-constraint`. |\n| `#::pythonpath` | One or more paths to prepend to `sys.path` when the build environment is created/executed. This is already supported by `kraken-core` but will be used to generate a `.pth` file when using the `VENV` environment type. The `./build-support/` will always be added to `sys.path`. |\n\n### Environment variables\n\nThe following environment variables are handled by kraken-wrapper:\n\n| Variable | Description |\n| -------- | ----------- |\n| `KRAKENW_USE` | If set, it will behave as if the `--use` flag was specified (although the `--use` flag if given will still take precedence over the environment variable). Can be used to enforce a certain type of build environment to use. Available values are `PEX_ZIPAPP`, `PEX_PACKED`, `PEX_LOOSE` and `VENV` (default). |\n| `KRAKENW_REINSTALL` | If set to `1`, behaves as if `--reinstall` was specified. |\n| `KRAKENW_INCREMENTAL` |  If set to `1`, virtual environment build environments are "incremental", i.e. they will be reused if they already exist and their installed distributions will be upgraded. |\n\n### Recommendations\n\n* When using local requirements, using the `VENV` type is a lot fast because it can leverage Pip\'s `in-tree-build`\nfeature. Pex [does not currently support in-tree builds](https://github.com/pantsbuild/pex/issues/1357#issuecomment-860133766).\n\n### Index credentials\n\n  [keyring]: https://github.com/jaraco/keyring\n\nPip doesn\'t really have a good way to globally configure credentials for Python package indexes when they are not\nconfigured as an alias in `.piprc` aside from `~/.netrc`. Both of these methods have the drawback that the password\nis stored in plain text on disk. Pip does technically support looking up a password from the system keychain using\nthe [`keyring`][keyring] package, but it doesn\'t store the username and so will have to ask for it via stdin.\n\nTo work around this limitation, kraken-wrapper offers the `auth` command which allows you to configure credentials\nwhere the username is stored in `~/.config/krakenw/config.toml` and the password is stored in the system keychain\n(also using the [`keyring`][keyring] package).\n\n    $ krakenw auth example.jfrog.io -u my@email.org \n    Password for my@email.org:\n\n> __Important note__: If no backend for the `keyring` package is available, kraken-wrapper will fall back to writing\n> the password as plain text into the same configuration file.\n',
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
