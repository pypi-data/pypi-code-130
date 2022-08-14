# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pytest_ebics_sandbox']

package_data = \
{'': ['*']}

install_requires = \
['docker>=5.0.3,<6.0.0', 'requests>=2.28.1,<3.0.0']

entry_points = \
{'pytest11': ['ebics_sandbox = pytest_ebics_sandbox']}

setup_kwargs = {
    'name': 'pytest-ebics-sandbox',
    'version': '0.1.1',
    'description': 'A pytest plugin for testing against an EBICS sandbox server. Requires docker.',
    'long_description': '# pytest-ebics-sandbox\n\nProvides one fixture `ebics_sandbox` of type `EbicsSandbox`.\n\nWill use docker to start a session-lived instance of libeufin-sandbox.\n',
    'author': 'Henryk Plötz',
    'author_email': 'henryk@ploetzli.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/henryk/pytest-ebics-sandbox',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
