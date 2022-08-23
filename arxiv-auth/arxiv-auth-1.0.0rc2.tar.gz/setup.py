# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arxiv_auth',
 'arxiv_auth.auth',
 'arxiv_auth.auth.sessions',
 'arxiv_auth.auth.sessions.tests',
 'arxiv_auth.auth.tests',
 'arxiv_auth.legacy',
 'arxiv_auth.legacy.tests',
 'arxiv_auth.tests']

package_data = \
{'': ['*']}

install_requires = \
['arxiv-base>=1.0.0a3',
 'flask',
 'flask-sqlalchemy',
 'mimesis',
 'mysqlclient',
 'pycountry',
 'pydantic',
 'pyjwt',
 'python-dateutil',
 'redis-py-cluster==1.3.6',
 'redis==2.10.6',
 'sqlalchemy']

setup_kwargs = {
    'name': 'arxiv-auth',
    'version': '1.0.0rc2',
    'description': 'Auth libraries for arXiv.',
    'long_description': None,
    'author': 'arxiv.org',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
