# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oxcgrt']

package_data = \
{'': ['*']}

install_requires = \
['opencovid19-api>=0.0.1,<0.0.2']

setup_kwargs = {
    'name': 'oxcgrt',
    'version': '0.0.1',
    'description': 'COVID-19 Data from OxCGRT wrapped by OpenCOVID-19',
    'long_description': '# oxcgrt\n\nCOVID-19 Data from OxCGRT wrapped by OpenCOVID-19\n\n\n\n## Installation\n\n```bash\npip install oxcgrt\n```\n\n\n\n## Quick Start\n\n```python\nimport oxcgrt\n```\n\n\n\n## Contributing\n\n\n\n',
    'author': 'OpenCOVID-19',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/opencovid19data/oxcgrt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
