# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['notus',
 'notus.scanner',
 'notus.scanner.cli',
 'notus.scanner.loader',
 'notus.scanner.messages',
 'notus.scanner.messaging',
 'notus.scanner.models',
 'notus.scanner.models.packages',
 'notus.scanner.tools',
 'tests',
 'tests.cli',
 'tests.loader',
 'tests.messages',
 'tests.messaging',
 'tests.models',
 'tests.models.packages']

package_data = \
{'': ['*']}

modules = \
['poetry']
install_requires = \
['packaging<21.3',
 'paho-mqtt>=1.6,<2.0',
 'psutil>=5.9,<6.0',
 'python-gnupg>=0.4.8,<0.5.0',
 'tomli<3.0.0']

extras_require = \
{'sentry': ['sentry-sdk>=1.6.0,<2.0.0']}

entry_points = \
{'console_scripts': ['notus-scan-start = notus.scanner.tools.scanstart:main',
                     'notus-scanner = notus.scanner.daemon:main',
                     'notus-subscriber = notus.scanner.tools.subscriber:main']}

setup_kwargs = {
    'name': 'notus-scanner',
    'version': '22.4.0',
    'description': 'A vulnerability scanner for creating results from local security checks (LSCs) ',
    'long_description': '![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_new-logo_horizontal_rgb_small.png)\n\n# Notus Scanner <!-- omit in toc -->\n\n[![Build and test](https://github.com/greenbone/notus-scanner/actions/workflows/ci-python.yml/badge.svg)](https://github.com/greenbone/notus-scanner/actions/workflows/ci-python.yml)\n[![codecov](https://codecov.io/gh/greenbone/notus-scanner/branch/main/graph/badge.svg?token=LaduLacbWO)](https://codecov.io/gh/greenbone/notus-scanner)\n\nNotus Scanner detects vulnerable products in a system environment. The scanning\nmethod is to evaluate internal system information. It does this very fast and\neven detects currently inactive products because it does not need to interact\nwith each of the products.\n\nTo report about vulnerabilities, Notus Scanner receives collected system\ninformation on the one hand and accesses the vulnerability information from the\nfeed service on the other. Both input elements are in table form: the system\ninformation is specific to each environment and the vulnerability information is\nspecific to each system type.\n\nNotus Scanner integrates into the Greenbone Vulnerability Management framework\nwhich allows to let it scan entire networks within a single task. Any\nvulnerability test in the format of `.notus` files inside the Greenbone Feed\nwill be considered and automatically matched with the scanned environments.\n\nA system environment can be the operating system of a host. But it could also be\ncontainers like Docker or virtual machines. Neither of these need to be actively\nrunning for scanning.\n\nThe Notus Scanner is implemented in Python and published under an Open Source\nlicense. Greenbone Networks maintains and extends it since it is embedded in the\nGreenbone Professional Edition as well as in the Greenbone Cloud Services.\n\nGreenbone also keeps the vulnerability information up-to-date via the feed on a\ndaily basis. The `.notus` format specification is open and part of the\ndocumentation.\n\n## Table of Contents <!-- omit in toc -->\n\n- [Installation](#installation)\n  - [Requirements](#requirements)\n- [Development](#development)\n- [Configuration](#configuration)\n- [Support](#support)\n- [Maintainer](#maintainer)\n- [Contributing](#contributing)\n- [License](#license)\n\n## Installation\n\n### Requirements\n\nPython 3.7 and later is supported.\n\nBesides Python Notus Scanner also needs to have\n\n- paho-mqtt\n- psutil\n- python-gnupg\n\ninstalled.\n\n## Development\n\n**notus-scanner** uses [poetry] for its own dependency management and build\nprocess.\n\nFirst install poetry via pip\n\n    python3 -m pip install --user poetry\n\nAfterwards run\n\n    poetry install\n\nin the checkout directory of **notus-scanner** (the directory containing the\n`pyproject.toml` file) to install all dependencies including the packages only\nrequired for development.\n\nAfterwards activate the git hooks for auto-formatting and linting via\n[autohooks].\n\n    poetry run autohooks activate\n\nValidate the activated git hooks by running\n\n    poetry run autohooks check\n\n## Configuration\n\nThe configuration of notus-scanner can be done by providing a TOML config file.\nPer default notus-scanner tries to load the settings from config files in the\nfollowing order: `~/.config/notus-scanner.toml`, `/etc/gvm/notus-scanner.toml`.\n\nAlternatively the location of the to be loaded config file can be set via the\n`-c`/`--config` command line argument. Setting a config file via command line\nwill ignore the default config files.\n\nThe settings are read from a `[notus-scanner]` [section](https://toml.io/en/v1.0.0#table).\n\nExample config file:\n```toml\n[notus-scanner]\nmqtt-broker-address = "1.2.3.4"\nmqtt-broker-port = "1234"\nproducts-directory = "/tmp/notus/advisories/products"\npid-file = "/tmp/notus-scanner.pid"\nlog-file = "/tmp/notus-scanner.log"\nlog-level = "DEBUG"\ndisable-hashsum-verification = true\n```\n\nEach setting can be overridden via an environment variable or command line\nargument.\n\n|Config|Environment|Default|Description|\n|------|-----------|-------|-----------|\n|log-file|NOTUS_SCANNER_LOG_FILE|syslog|File for log output|\n|log-level|NOTUS_SCANNER_LOG_LEVEL|INFO|Minimum level for log output|\n|mqtt-broker-address|NOTUS_SCANNER_MQTT_BROKER_ADDRESS|localhost|IP or DNS address of the MQTT broker|\n|mqtt-broker-port|NOTUS_SCANNER_MQTT_BROKER_PORT|1883|Port of the MQTT broker|\n|pid-file|NOTUS_SCANNER_PID_FILE|/run/notus-scanner/notus-scanner.pid|File for storing the process ID|\n|products-directory|NOTUS_SCANNER_PRODUCTS_DIRECTORY|/var/lib/openvas/plugins/notus/products|Directory for loading product advisories|\n|disable-hashsum-verification| NOTUS_DISABLE_HASHSUM_VERIFICATION | To disable hashsum verification of products |\n\n## Support\n\nFor any question on the usage of Notus Scanner please use the\n[Greenbone Community Portal]. If you found a problem with the software, please\ncreate an issue on GitHub. If you are a Greenbone customer you may alternatively\nor additionally forward your issue to the Greenbone Support Portal.\n\n## Maintainer\n\nThis project is maintained by [Greenbone Networks GmbH][Greenbone Networks]\n\n## Contributing\n\nYour contributions are highly appreciated. Please\n[create a pull request](https://github.com/greenbone/notus-scanner/pulls)\non GitHub. Bigger changes need to be discussed with the development team via the\n[issues section at GitHub](https://github.com/greenbone/notus-scanner/issues)\nfirst.\n\n## License\n\nCopyright (C) 2021-2022 Greenbone Networks GmbH\n\nLicensed under the GNU Affero General Public License v3.0 or later.\n\n[Greenbone Networks]: https://www.greenbone.net/\n[poetry]: https://python-poetry.org/\n[pip]: https://pip.pypa.io/\n[autohooks]: https://github.com/greenbone/autohooks\n[Greenbone Community Portal]: https://community.greenbone.net/\n',
    'author': 'Greenbone Networks GmbH',
    'author_email': 'info@greenbone.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/greenbone/notus-scanner',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
