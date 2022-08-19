# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['moirai', 'moirai.database', 'moirai.hardware', 'moirai.webapi']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.1,<3.0.0',
 'ahio>=1.0.27,<2.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'cheroot>=8.5.2,<9.0.0',
 'numpy>=1.21.0,<2.0.0',
 'pymongo>=3.11.4,<4.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'scipy>=1.9.0,<2.0.0']

entry_points = \
{'console_scripts': ['moirai = moirai.moirai:start']}

setup_kwargs = {
    'name': 'moirai',
    'version': '1.3.20',
    'description': 'Digital Control Manager Backend',
    'long_description': '# moirai\n\nMoirai is the backend for the platform. It is developed as part of my scientific\ninitiation project, named Plataformas de baixo custo para controle de processos\n(low-cost platform for process control), developed at CEFET-MG (Brazil) under\nthe supervision of Prof. Dr. Valter Leite. The project was developed through a\nFAPEMIG scholaship.\n\nIt\'s meant to be installed in a computer near the plant, so it can be\nremote-controlled by [Lachesis](https://github.com/acristoffers/Lachesis). It\nexposes a RESTful API that let\'s you configure the hardware, save tests and\ncontrollers, execute them and fetch the results in real-time or after the\nexecution finishes.\n\nControllers for this platform are written in Python 3 and can use any librarie\navailable in the computer where _moirai_ is running. It already depends on NumPy\nand SciPy, as they are commonly used. This platform manages the hardware\ninterfacing through the [ahio](https://github.com/acristoffers/ahio) libray, so\nextending it\'s hardware capabilities is a question of extending AHIO, which\nshould be simple. Execution time, sampling time, input querying and output\nupdating is managed by the application and let\'s you focus on your\ncontroller/model.\n\n## Installation\n\nUse pip to install. This is a Python 3 application and won\'t run in Python 2.\nUse `pip install moirai` or `pip3 install moirai` to install it. It also has\nother dependencies not installable through pip, which can be installed by\nrunning `moirai --install --sudo`. It will install MongoDB (or MySQL on\nRaspberry Pi) and the Snap7 library. It\'s designed to work on Windows, macOS\n(with Homebrew) and Linux (apt-get, dnf, yum and zypper).\n\nIf using the Snap7 driver on Windows, you may need to compile the driver\nyourself and copy it to /Windows/System32.\n\nOn macOS, using Homebrew, you can install with:\n\n```bash\nbrew tap acristoffers/repo\nbrew install moirai\n```\n\n## License\n\nCopyright (c) 2016 Álan Crístoffer\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in\nall copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN\nTHE SOFTWARE.\n',
    'author': 'Álan Crístoffer',
    'author_email': 'acristoffers@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/acristoffers/moirai',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
