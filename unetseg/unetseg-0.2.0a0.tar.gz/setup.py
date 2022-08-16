# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['unetseg', 'unetseg.console']

package_data = \
{'': ['*']}

install_requires = \
['albumentations>=1.1.0,<2.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'opencv-python>=4.5.5,<5.0.0',
 'rasterio>=1.2.10,<2.0.0',
 'scikit-image>=0.19.2,<0.20.0',
 'scikit-learn>=1.0.2,<2.0.0',
 'tensorflow>=2.4',
 'tifffile>=2022.2.9,<2023.0.0',
 'tqdm>=4.62.3,<5.0.0']

setup_kwargs = {
    'name': 'unetseg',
    'version': '0.2.0a0',
    'description': 'U-Net semantic segmentation for satellite imagery',
    'long_description': None,
    'author': 'Damián Silvani',
    'author_email': 'munshkr@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
