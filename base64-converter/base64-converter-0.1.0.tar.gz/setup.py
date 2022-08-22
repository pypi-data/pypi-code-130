# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['base64_converter']

package_data = \
{'': ['*']}

install_requires = \
['typer[all]>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['base64-converter = base64_converter.main:app']}

setup_kwargs = {
    'name': 'base64-converter',
    'version': '0.1.0',
    'description': '',
    'long_description': "# Base64 Converter\n\n`base64-converter` is a CLI tool to quickly Base64 encode and decode strings.\n\n## Installation - TBD\n\n```bash\npip install --user <TBD>\n```\n\n## Usage\n\n```bash\nUsage: base64-converter [OPTIONS] COMMAND [ARGS]...\n\nBase64 Converter\n\nOptions:\n    --install-completion          Install completion for the current shell.\n    --show-completion             Show completion for the current shell, to copy it or customize the installation.\n    --help                        Show this message and exit.\n\nCommands:\n    d                             Base64 decode\n    e                             Base64 encode\n```\n\n## Examples\n\n### Base64 Encode\n\n```bash\n$ base64-converter e test\n\nOutput: dGVzdA==\n```\n\n### Base64 Decode\n\n```bash\n$ base64-converter e dGVzdA==\n\nOutput: test\n```\n\n## Tips & Tricks\n\nI recommend shorthanding the CLI tool command. Be the lazy programmer.\n\n```bash\n# Linux/MacOS\n$ alias b=base64-converter\n\n# Windows\n$ add alias base64-converter b\n\n# Run Base64 Encode\n$ b e test\n\nOutput: dGVzdA==\n\n# Run Base64 Decode\n$ b d dGVzdA==\n\nOutput: test\n```\n\n## Contributing\n\nTo make a contribution, fork the repo, make your changes and then submit a pull request. Please try to adhere to the existing style. If you've discovered a bug or have a feature request, create an issue.\n\nPending Features:\n\n- Support iterations to allow multiple encoding/decoding in a single line.\n\n## How it Works\n\nBase64 Converter is written in Python and built on Typer. Typer is a library for building CLI applications.\n",
    'author': 'johnyacuta',
    'author_email': 'example@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
