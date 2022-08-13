# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shortfun']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'shortfun',
    'version': '0.0.1',
    'description': 'Short lambda functions for built in operations',
    'long_description': '```py\nfrom shortfun import sf\n\n>>> filtered = filter(sf.gt(10), [1, 20, 10, 8, 30])\n>>> list(filtered)\n[20, 30]\n```\n\n```py\nfrom shortfun import _\n\n>>> mapped = map(sf.add(10), [1, 20, 10, 8, 30])\n>>> list(mapped)\n[11, 30, 20, 18, 40]\n```\nUsing the shorter-hand method:\n\n```py\nfrom shortfun import _\n\n>>> filtered = filter(_ > 10, [1, 20, 10, 8, 30])\n>>> list(filtered)\n[20, 30]\n```\n\n```py\nfrom shortfun import _\n\n>>> mapped = map(_ + 10, [1, 20, 10, 8, 30])\n>>> list(mapped)\n[11, 30, 20, 18, 40]\n```\n',
    'author': 'Alex Rudolph',
    'author_email': 'alex3rudolph@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.github.com/alrudolph/shortfun',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
