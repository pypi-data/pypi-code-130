# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shortfun']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'shortfun',
    'version': '0.1.0',
    'description': 'Short lambda functions for functional built in operations',
    'long_description': '# `shortfun`\n\nThis package provides a functional way to use python operators. Using this package would prevent the need to do something such as:\n\n```py\nlambda x: x + 10\n```\n\nwhere we use a lambda function to pass in arguments to a function (in this case +) one at a time.\n\n## Examples:\n\n```py\n>>> from shortfun import sf\n\n>>> filtered = filter(sf.gt(10), [1, 20, 10, 8, 30]) # Greater-than function\n>>> list(filtered)\n[20, 30]\n```\n\n```py\n>>> from shortfun import sf\n\n>>> mapped = map(sf.add(10), [1, 20, 10, 8, 30]) # Addition function\n>>> list(mapped)\n[11, 30, 20, 18, 40]\n```\nUsing the shorter-hand method:\n\n## Even Shorter Functions\n\nThis API is more limited, but in certain situations you can use the underscore variable provided by this function as a replacement for `lambda x: x ...`\n\n```py\n>>> from shortfun import _\n\n>>> filtered = filter(_ > 10, [1, 20, 10, 8, 30])\n>>> list(filtered)\n[20, 30]\n```\n\n```py\n>>> from shortfun import _\n\n>>> mapped = map(_ + 10, [1, 20, 10, 8, 30])\n>>> list(mapped)\n[11, 30, 20, 18, 40]\n```\n',
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
