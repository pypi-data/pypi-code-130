# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['volttron',
 'volttron.client',
 'volttron.client.commands',
 'volttron.client.messaging',
 'volttron.client.vip',
 'volttron.client.vip.agent',
 'volttron.client.vip.agent.subsystems',
 'volttron.server',
 'volttron.server.router',
 'volttron.services.auth',
 'volttron.services.config_store',
 'volttron.services.control',
 'volttron.services.external',
 'volttron.services.health',
 'volttron.services.peer',
 'volttron.services.pubsub',
 'volttron.services.routing',
 'volttron.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'cryptography>=36.0.1,<37.0.0',
 'dateutils>=0.6.12,<0.7.0',
 'gevent>=21.12.0,<22.0.0',
 'psutil>=5.9.0,<6.0.0',
 'pyzmq>=22.3.0,<23.0.0',
 'toml>=0.10.2,<0.11.0',
 'tzlocal>=4.1,<5.0',
 'watchdog-gevent>=0.1.1,<0.2.0']

entry_points = \
{'console_scripts': ['vcfg = volttron.client.commands.config:main',
                     'vctl = volttron.client.commands.control:main',
                     'volttron = volttron.server.__main__:main',
                     'volttron-cfg = volttron.client.commands.config:main',
                     'volttron-ctl = volttron.client.commands.control:main']}

setup_kwargs = {
    'name': 'volttron',
    'version': '10.0.1a17',
    'description': '',
    'long_description': 'None',
    'author': 'volttron',
    'author_email': 'volttron@pnnl.gov',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
