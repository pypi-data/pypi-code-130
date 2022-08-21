# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['asttrs']

package_data = \
{'': ['*']}

install_requires = \
['astor', 'attrs', 'black', 'cattrs', 'isort']

setup_kwargs = {
    'name': 'asttrs',
    'version': '0.7.0',
    'description': 'A attrs-style wrapper for python ast',
    'long_description': '# asttrs\nA attrs-style wrapper for python ast\n',
    'author': 'ryanchao2012',
    'author_email': 'ryanchao2012@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ryanchao2012/asttrs',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
