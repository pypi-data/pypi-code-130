# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cmem_plugin_examples',
 'cmem_plugin_examples.transform',
 'cmem_plugin_examples.workflow']

package_data = \
{'': ['*']}

install_requires = \
['cmem-cmempy>=22.1', 'cmem-plugin-base>=2.1.0,<3.0.0']

setup_kwargs = {
    'name': 'cmem-plugin-examples',
    'version': '0.0.9',
    'description': 'Example plugins for eccenca Corporate Memory.',
    'long_description': '# cmem-plugin-examples\n\nExample plugins for eccenca Corporate Memory.\n\n',
    'author': 'eccenca',
    'author_email': 'cmempy-developer@eccenca.com',
    'maintainer': 'Sebastian Tramp',
    'maintainer_email': 'sebastian.tramp@eccenca.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
