# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ranzen',
 'ranzen.hydra',
 'ranzen.torch',
 'ranzen.torch.optimizers',
 'ranzen.torch.transforms']

package_data = \
{'': ['*']}

extras_require = \
{'all': ['torch>=1.8,<2.0',
         'hydra-core>=1.2.0,<2.0.0',
         'neoconfigen>=2.3.3',
         'numpy>=1.21.4,<2.0.0',
         'pandas>=1.4.3,<2.0.0',
         'wandb>=0.12,<0.14'],
 'hydra': ['hydra-core>=1.2.0,<2.0.0', 'neoconfigen>=2.3.3'],
 'torch': ['torch>=1.8,<2.0', 'numpy>=1.21.4,<2.0.0'],
 'wandb': ['pandas>=1.4.3,<2.0.0', 'wandb>=0.12,<0.14']}

setup_kwargs = {
    'name': 'ranzen',
    'version': '2.0.1',
    'description': 'A toolkit facilitating machine-learning experimentation.',
    'long_description': '# ranzen 🎒\n\nA python toolkit facilitating machine-learning experimentation.\n\n[Documentation](https://wearepal.github.io/ranzen/)\n\n## Install\n\nRun\n```\npip install ranzen\n```\n\nor install directly from GitHub:\n```\npip install git+https://github.com/predictive-analytics-lab/ranzen.git@main\n```\n',
    'author': 'PAL',
    'author_email': 'info@predictive-analytics-lab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/predictive-analytics-lab/ranzen',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.8.0,<3.11',
}


setup(**setup_kwargs)
