# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'lib'}

packages = \
['big_slpp']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'big-slpp',
    'version': '1.0.0',
    'description': "SirAnthony's SLPP, but modernized code (also, trailing comma's)",
    'long_description': None,
    'author': 'NostraDavid',
    'author_email': '55331731+nostradavid@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
