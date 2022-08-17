# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fsdev']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0']

entry_points = \
{'console_scripts': ['fsdev = fsdev.cli:run']}

setup_kwargs = {
    'name': 'fsdev',
    'version': '0.1.1',
    'description': 'A super simple filesystem dev server',
    'long_description': '# fsdev\n\nA super simple filesystem dev server.\n\n## Usage\n\nAbsolutely zero configuration. Just type `fsdev` in the directory you want to serve. Static files go in `static` and templates go in `templates`. You can make templates *private* (hide from server) by prepending with an underscore (e.g., `_header.html`). This is great for partials.\n\n## Known Issues\n\n-   Import warning on serve\n\n## Documentation\n\nDocumentation in Markdown. Configured to use pdoc documentation tool:\n\n```\npoetry run pdoc fsdev.py\n```\n',
    'author': 'Tristan Slater',
    'author_email': 'hello@trslater.ca',
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
