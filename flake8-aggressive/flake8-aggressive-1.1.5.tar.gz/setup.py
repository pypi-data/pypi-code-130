# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flake8_aggressive']

package_data = \
{'': ['*']}

install_requires = \
['darglint>=1.8.1',
 'flake8-2020>=1.7.0',
 'flake8-absolute-import>=1.0.0.1',
 'flake8-annotations-complexity>=0.0.7',
 'flake8-annotations>=2.9.1',
 'flake8-bandit>=3.0.0',
 'flake8-blind-except>=0.2.1',
 'flake8-breakpoint>=1.1.0',
 'flake8-broken-line>=0.5.0',
 'flake8-bugbear>=22.7.1',
 'flake8-builtins>=1.5.3',
 'flake8-class-attributes-order>=0.1.3',
 'flake8-comprehensions>=3.10.0',
 'flake8-datetimez>=20.10.0',
 'flake8-debugger>=4.1.2',
 'flake8-eradicate>=1.3.0',
 'flake8-executable>=2.1.1',
 'flake8-expression-complexity>=0.0.11',
 'flake8-fixme>=1.1.1',
 'flake8-if-expr>=1.0.4',
 'flake8-isort>=4.2.0',
 'flake8-logging-format>=0.7.4',
 'flake8-no-implicit-concat>=0.3.3',
 'flake8-pep3101>=1.3.0',
 'flake8-print>=5.0.0',
 'flake8-pytest-style>=1.6.0',
 'flake8-pytest>=1.4',
 'flake8-raise>=0.0.5',
 'flake8-requirements>=1.6.0',
 'flake8-return>=1.1.3',
 'flake8-simplify>=0.19.3',
 'flake8-strftime>=0.3.2',
 'flake8-string-format>=0.3.0',
 'flake8-super>=0.1.3',
 'flake8-use-pathlib>=0.3.0',
 'flake8>=4.0.1',
 'flakeheaven>=1.0.1',
 'pep8-naming>=0.13.1',
 'pylint>=2.14.5']

setup_kwargs = {
    'name': 'flake8-aggressive',
    'version': '1.1.5',
    'description': 'Flake8 aggressive plugins pack',
    'long_description': "# flake8-aggressive\n\n[![pypi](https://badge.fury.io/py/flake8-aggressive.svg)](https://pypi.org/project/flake8-aggressive)\n[![Python: 3.6+](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://pypi.org/project/flake8-aggressive)\n[![Downloads](https://img.shields.io/pypi/dm/flake8-awesome.svg)](https://pypistats.org/packages/flake8-aggressive)\n[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://en.wikipedia.org/wiki/MIT_License)\n\nFlake8 aggressive plugins pack. This is a fork of the very awesome [flake8-awesome](https://github.com/afonasev/flake8-awesome) plugins pack. This one is intended to\ninclude a lot more plugins.\n\n## Installation\n\n```bash\npip install flake8-aggressive\n```\n\nvs\n\n```bash\npip install flake8 flake8-builtins flake8-comprehensions flake8-eradicate # etc.\n```\n\n## Example of Flake8 config\n\n```ini\n[flake8]\nenable-extensions = G\nexclude = .git, .venv\nignore =\n    A003 ; 'id' is a python builtin, consider renaming the class attribute\n    W503 ; line break before binary operator\n    S101 ; use of assert detected (useless with pytest)\nmax-complexity = 8\nmax-annotations-complexity = 3\nmax-expression-complexity = 7\nmax-line-length = 120\nshow-source = true\n```\n\n## List of plugins\n\n### flake8-awesome\n\n* flake8-annotations-complexity\n* flake8-bandit\n* flake8-breakpoint\n* flake8-bugbear\n* flake8-builtins\n* flake8-comprehensions\n* flake8-eradicate\n* flake8-expression-complexity\n* flake8-if-expr\n* flake8-isort\n* flake8-logging-format\n* flake8-print\n* flake8-pytest\n* flake8-pytest-style\n* flake8-requirements\n* flake8-return\n* pep8-naming\n\n### flake8-aggressive\n\n* pylint\n* flakeheaven\n* darglint\n* flake8-2020\n* flake8-absolute-import\n* flake8-annotations\n* flake8-blind-except\n* flake8-broken-line\n* flake8-class-attributes-order\n* flake8-datetimez\n* flake8-debugger\n* flake8-executable\n* flake8-fixme\n* flake8-no-implicit-concat\n* flake8-pep3101\n* flake8-raise\n* flake8-simplify\n* flake8-strftime\n* flake8-string-format\n* flake8-super\n* flake8-use-pathlib\n",
    'author': 'Austin Page',
    'author_email': 'jaustinpage@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/flake8-aggreessive',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
