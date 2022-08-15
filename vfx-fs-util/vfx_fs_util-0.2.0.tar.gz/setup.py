# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['vfx_fs_util', 'vfx_fs_util.compressed_filepath']

package_data = \
{'': ['*']}

install_requires = \
['Lucidity>=1.6.0,<2.0.0', 'scandir>=1.10.0,<2.0.0']

entry_points = \
{'console_scripts': ['fsu = vfx_fs_util.__main__:main']}

setup_kwargs = {
    'name': 'vfx-fs-util',
    'version': '0.2.0',
    'description': 'Utility package for working filesystems in the VFX industry.',
    'long_description': None,
    'author': 'John Andrews',
    'author_email': 'john.andrews.drum@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
