# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['beautifulplots']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4', 'pandas>=1.0', 'seaborn>=0.9']

setup_kwargs = {
    'name': 'beautifulplots',
    'version': '0.2.1',
    'description': 'Python plotting library for beautiful, easy, and sophisticated matplotlib based plots. Compatible with Pandas and Seaborn plots.',
    'long_description': '# beautifulplots\n\nPython plotting library for beautiful, easy, and sophisticated matplotlib based plots. Compatible with Matplotlib graphs, such as Pandas and Seaborn.\n\n## Motivation\nData scientists use data visualization for analysis, investigation, insight, and story telling. In this endeavor, Matplotlib based plotting libraries are reputedly the most powerful and customizable. However, creating graphs for analysis, though necessary, often diverges from the primary goal. Furthermore, Graphs resulting from data science analysis inevitably populate reports, presentations, and even interactive web graphics. After some experience, use case after use case requires similar supporting code. \n\n## Goal\nThe goal of the beautifulplots plotting library is to package graphing functions for the easy generation of beautiful graphs without the burden of distracting code.\n\n## Installation\n\n```bash\n$ pip install beautifulplots\n```\n\n## Usage and Examples\n\n- See usage examples in examples.ipynb (Jupyter notebook) and readthedocs [beatifulplots readthedocs](https://beautifulplots.readthedocs.io/en/latest/index.html).\n\n\n## Feature Requests and Issues\n\nFeature requests and issues: please provide feedback and suggestions for improvements or issues via github issues [new issue](https://github.com/Aljgutier/beautifulplots/issues).\n\n\n## License\n\n`beautifulplots` was created by Alberto Gutierrez. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`beautifulplots` package setup with  [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Alberto Gutierrez',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
