# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['guipy', 'guipy.components']

package_data = \
{'': ['*']}

install_requires = \
['pygame>=2.1.2,<3.0.0']

setup_kwargs = {
    'name': 'guipylib',
    'version': '0.0.0',
    'description': 'UI library for pygame',
    'long_description': '# Guipy\nPygame UI Library built by Casey (@caseyhackerman) and Jason\n',
    'author': 'Casey Culbertson, Jason Zhang',
    'author_email': 'me@jasonzhang.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Zjjc123/guipy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
