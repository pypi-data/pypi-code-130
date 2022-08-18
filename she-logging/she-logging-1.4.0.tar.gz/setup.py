# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['she_logging']

package_data = \
{'': ['*']}

install_requires = \
['JSON-log-formatter<1.0.0', 'PyYAML>=5.0.0,<6.0.0', 'environs']

extras_require = \
{':python_full_version >= "3.6.0" and python_full_version < "3.7.0"': ['contextvars>=2.0.0,<3.0.0'],
 'colour': ['rich>=10.0.0,<11.0.0']}

entry_points = \
{'gunicorn.loggers': ['gunicorn = she_logging.gunicorn_logger:Logger']}

setup_kwargs = {
    'name': 'she-logging',
    'version': '1.4.0',
    'description': 'Common logging configuration for Polaris microservices',
    'long_description': None,
    'author': 'Duncan Booth',
    'author_email': 'duncan.booth@sensynehealth.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/draysontechnologies/she-logging',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.9,<4.0',
}


setup(**setup_kwargs)
