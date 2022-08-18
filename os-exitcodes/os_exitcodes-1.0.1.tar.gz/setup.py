# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['os_exitcodes']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'os-exitcodes',
    'version': '1.0.1',
    'description': 'A cross-operating-system compatible library for os.EX_* constants',
    'long_description': '# Exit Codes\n\nThis package is a cross-operating-system compatible version of the `os` library\'s EX\\_\\* constants.\n\nIf these constants are available, they will be re-exported directly from `os`, otherwise the integer version will be provided from this library.\n\nThis library also provides an enum version of the exit codes, if that is of value.\n\nApologies for the weird PyPi name, they\'re a bit overly restrictive and don\'t point to what specifically is the conflicting package.\n\n## Installation\n\n```shell\npython -m pip install -U os-exitcodes\n```\n\n## Usage\n\n### Constants\n\n```python\nfrom os_exitcodes import (\n    EX_OK,\n    EX_USAGE,\n)\nfrom random import choice\n\ndef is_valid_usage() -> bool:\n    # check if the user is using this properly\n    # for a working example, this is random\n    return choice([True, False])\n\ndef main() -> None:\n    invalid_usage = random\n    if not is_valid_usage():\n        raise SystemExit(EX_USAGE)\n    raise SystemExit(EX_OK)\n\nif __name__ == "__main__":\n    main()\n```\n\n### Enumeration\n\n```python\nfrom os_exitcodes import ExitCode\nfrom random import choice\n\ndef is_valid_usage() -> bool:\n    # check if the user is using this properly\n    # for a working example, this is random\n    return choice([True, False])\n\ndef main() -> None:\n    invalid_usage = random\n    if not is_valid_usage():\n        raise SystemExit(ExitCode.EX_USAGE)\n    raise SystemExit(ExitCode.EX_OK)\n\nif __name__ == "__main__":\n    main()\n```\n',
    'author': 'Kevin Kirsche',
    'author_email': 'kev.kirsche@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kkirsche/os-exitcodes',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
