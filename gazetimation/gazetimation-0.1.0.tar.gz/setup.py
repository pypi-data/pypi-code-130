# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['gazetimation']
install_requires = \
['mediapipe>=0.8.10,<0.9.0',
 'numpy>=1.23.2,<2.0.0',
 'opencv-python>=4.6.0,<5.0.0']

setup_kwargs = {
    'name': 'gazetimation',
    'version': '0.1.0',
    'description': 'Gaze estimation from facial landmarks',
    'long_description': '',
    'author': 'Shuvo Kumar Paul',
    'author_email': 'shuvo.k.paul@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/paul-shuvo/gazetimation',
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
