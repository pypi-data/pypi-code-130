# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jhu_csse']

package_data = \
{'': ['*']}

install_requires = \
['opencovid19-api>=0.0.1,<0.0.2']

setup_kwargs = {
    'name': 'jhu-csse',
    'version': '0.0.1',
    'description': 'COVID-19 Data from JHU CSSE wrapped by OpenCOVID-19',
    'long_description': '# jhu-csse\n\nCOVID-19 Data from JHU CSSE wrapped by OpenCOVID-19\n\n\n\n## Installation\n\n```bash\npip install jhu-csse\n```\n\n\n\n## Quick Start\n\n```python\nimport jhu_csse\n```\n\n\n\n## Contributing\n\n\n\n',
    'author': 'OpenCOVID-19',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/opencovid19data/jhu-csse',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
