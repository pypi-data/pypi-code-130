# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mkreadme']

package_data = \
{'': ['*'], 'mkreadme': ['static/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.1.3,<9.0.0',
 'inquirer>=2.10.0,<3.0.0',
 'pydantic>=1.9.2,<2.0.0']

entry_points = \
{'console_scripts': ['mkreadme = mkreadme.__main__:main']}

setup_kwargs = {
    'name': 'mkreadme',
    'version': '0.3.0',
    'description': 'A cli tool to interactively generate a README file',
    'long_description': '# mkreadme\n\n## 📝 Description\n\n`mkreadme` is a cli tool for interactive creation of a `README.md` file. It was inspired by [readme.so](https://readme.so/). You can choose from different `README` sections, which are then merged into a complete document.\n\n## ⚙️ Installation\n\nInstall `mkreadme` with `pip`\n\n```bash\n  pip install mkreadme\n```\n\n## 💡 Usage Examples\n\nTo interactively create a README file with `mkreadme`, run\n\n```console\nmkreadme --filename README.md\n```\n\n## 🖼️ Screenshots\n\n![App Screenshot](static/Screenshot.png)\n',
    'author': 'An Hoang',
    'author_email': 'anhoang31415@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
