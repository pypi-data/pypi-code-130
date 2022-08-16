# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opencovid19']

package_data = \
{'': ['*']}

install_requires = \
['opencovid19-api>=0.0.1,<0.0.2']

setup_kwargs = {
    'name': 'opencovid19',
    'version': '0.0.1',
    'description': 'COVID-19 Data wrapped by OpenCOVID-19',
    'long_description': '# opencovid19\n\nCOVID-19 Data wrapped by OpenCOVID-19\n\n\n\n## Installation\n\n```bash\npip install opencovid19\n```\n\n\n\n## Quick Start\n\n```python\nimport opencovid19\n```\n\n\n\n## Contributing\n\n\n\n',
    'author': 'OpenCOVID-19',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/opencovid19data/opencovid19',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
