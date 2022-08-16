# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['opencovid19_api']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'opencovid19-api',
    'version': '0.0.1',
    'description': 'OpenCOVID-19 API for COVID-19 Data',
    'long_description': '# opencovid19-api\n\nOpenCOVID-19 API for COVID-19 Data\n\n\n\n## Installation\n\n```bash\npip install opencovid19-api\n```\n\n\n\n## Quick Start\n\n```python\nimport opencovid19_api\n```\n\n\n\n## Contributing\n\n\n\n',
    'author': 'OpenCOVID-19',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/opencovid19data/opencovid19-api',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
