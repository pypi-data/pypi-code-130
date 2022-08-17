# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['io_orbit',
 'io_orbit.events',
 'io_orbit.firebase_config',
 'io_orbit.logger',
 'io_orbit.workflow']

package_data = \
{'': ['*']}

install_requires = \
['firebase-admin>=5.2.0,<6.0.0',
 'gcsfs>=2022.1.0,<2023.0.0',
 'pika>=1.2.0,<2.0.0',
 'requests>=2.25.1,<3.0.0']

entry_points = \
{'console_scripts': ['io-orbit = io_orbit:main']}

setup_kwargs = {
    'name': 'io-orbit',
    'version': '0.0.6',
    'description': 'Simple and flexible ML workflow engine',
    'long_description': '# ioOrbit\n\n## Overview\n\nSimple and flexible ML workflow engine. This library is meant to wrap all reusable code to simplify workflow implementation.\n\nSupported functionality:\n\n- Flexible logger \n- Firebase-admin / GCSFS file system handler\n- API to communicate with RabbitMQ for event receiver/producer\n- Workflow call helper\n- Logger call helper\n\n\n## License\n\nLicensed under the Apache License, Version 2.0.',
    'author': 'laccuna',
    'author_email': 'team@laccuna.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
