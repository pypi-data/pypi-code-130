# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['param']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tombulled-param',
    'version': '0.1.0',
    'description': 'Enhanced function parameters',
    'long_description': '# param\nEnhanced function parameters\n\n## Installation\n```sh\npip install git+https://github.com/tombulled/param.git@main\n```\n\n## Usage\n```python\nfrom param import Param, params\n\n@params\ndef get(url: str, params: dict = Param(default_factory=dict)):\n    print("GET", url, params)\n```\n```python\n>>> get("https://httpbin.com/get")\nGET https://httpbin.com/get {}\n```',
    'author': 'Tom Bulled',
    'author_email': '26026015+tombulled@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/param/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
