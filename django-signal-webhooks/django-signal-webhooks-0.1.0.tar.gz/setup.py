# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['signal_webhooks', 'signal_webhooks.migrations']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.1',
 'asgiref>=3.5.0',
 'cryptography>=36.0.0',
 'django-settings-holder>=0.0.4',
 'httpx>=0.23.0']

setup_kwargs = {
    'name': 'django-signal-webhooks',
    'version': '0.1.0',
    'description': 'Add webhooks to django using signals.',
    'long_description': '# Django Signal Webhooks\n\n[![Coverage Status][coverage-badge]][coverage]\n[![GitHub Workflow Status][status-badge]][status]\n[![PyPI][pypi-badge]][pypi]\n[![GitHub][licence-badge]][licence]\n[![GitHub Last Commit][repo-badge]][repo]\n[![GitHub Issues][issues-badge]][issues]\n[![Downloads][downloads-badge]][pypi]\n\n[![Python Version][version-badge]][pypi]\n[![Django Version][django-badge]][pypi]\n\n```shell\npip install django-signal-webhooks\n```\n\n---\n\n**Documentation**: [https://mrthearman.github.io/django-signal-webhooks/](https://mrthearman.github.io/django-signal-webhooks/)\n\n**Source Code**: [https://github.com/MrThearMan/django-signal-webhooks/](https://github.com/MrThearMan/django-signal-webhooks/)\n\n---\n\nThis library enables you to add webhooks to a Django project for any create/update/delete\nevents on your models with a simple configuration. New webhooks can be added in the\nadmin panel, with or without authentication, with plenty of hooks into the webhook sending\nprocess to customize them for your needs.\n\n```python\n# project/settings.py\n\n# Add to instaled apps\nINSTALLED_APPS = [\n    ...\n    "signal_webhooks",\n    ...\n]\n\n# Add default webhook configuration to the User model\nSIGNAL_WEBHOOKS = {\n    "HOOKS": {\n        "django.contrib.auth.models.User": ...,\n    },\n}\n```\n\n[coverage-badge]: https://coveralls.io/repos/github/MrThearMan/django-signal-webhooks/badge.svg?branch=main\n[status-badge]: https://img.shields.io/github/workflow/status/MrThearMan/django-signal-webhooks/Test\n[pypi-badge]: https://img.shields.io/pypi/v/django-signal-webhooks\n[licence-badge]: https://img.shields.io/github/license/MrThearMan/django-signal-webhooks\n[repo-badge]: https://img.shields.io/github/last-commit/MrThearMan/django-signal-webhooks\n[issues-badge]: https://img.shields.io/github/issues-raw/MrThearMan/django-signal-webhooks\n[version-badge]: https://img.shields.io/pypi/pyversions/django-signal-webhooks\n[downloads-badge]: https://img.shields.io/pypi/dm/django-signal-webhooks\n[django-badge]: https://img.shields.io/pypi/djversions/django-signal-webhooks\n\n[coverage]: https://coveralls.io/github/MrThearMan/django-signal-webhooks?branch=main\n[status]: https://github.com/MrThearMan/django-signal-webhooks/actions/workflows/test.yml\n[pypi]: https://pypi.org/project/django-signal-webhooks\n[licence]: https://github.com/MrThearMan/django-signal-webhooks/blob/main/LICENSE\n[repo]: https://github.com/MrThearMan/django-signal-webhooks/commits/main\n[issues]: https://github.com/MrThearMan/django-signal-webhooks/issues\n',
    'author': 'Matti Lamppu',
    'author_email': 'lamppu.matti.akseli@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://mrthearman.github.io/django-signal-webhooks/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
