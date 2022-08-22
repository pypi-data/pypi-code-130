# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['services',
 'services.commands',
 'services.db',
 'services.security',
 'services.templates',
 'services.templates.alembic',
 'services.templates.app',
 'services.users']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'PyJWT>=2.4.0,<3.0.0',
 'SQLAlchemy>=1.4.39,<2.0.0',
 'alembic>=1.8.1,<2.0.0',
 'cryptography>=37.0.4,<38.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'rich>=12.5.1,<13.0.0',
 'sanic[ext]>=22.6.0,<23.0.0']

entry_points = \
{'console_scripts': ['srv = services.cli:cli']}

setup_kwargs = {
    'name': 'ai-services',
    'version': '0.2.0',
    'description': 'A simple web framework based on Sanic',
    'long_description': None,
    'author': 'nuxion',
    'author_email': 'nuxion@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nuxion/services',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
