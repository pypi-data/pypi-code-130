# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['thundercougarfalconbird']

package_data = \
{'': ['*']}

install_requires = \
['numpy', 'squaternion']

setup_kwargs = {
    'name': 'thundercougarfalconbird',
    'version': '0.0.4',
    'description': 'ode integration rk4 rk runge kutta',
    'long_description': '![](https://github.com/MomsFriendlyRobotCompany/thundercougarfalconbird/raw/main/pics/eddy.png)\n\n![GitHub](https://img.shields.io/github/license/MomsFriendlyRobotCompany/thundercougarfalconbird)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/thundercougarfalconbird)\n![PyPI](https://img.shields.io/pypi/v/thundercougarfalconbird)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/thundercougarfalconbird?color=aqua)\n\n# Just one word, `thundercougarfalconbird`\n\n**under development**\n\nSome of the dynamical models available are:\n\n- `DifferentialDriveKinematics`\n- `Drone`\n    - `ParrotDrone`\n\nThe list of imported packages can be found in the [pyproject.toml][toml].\n\n# MIT License\n\n**Copyright (c) 2022 Mom\'s Friendly Robot Company**\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n\n[toml]: https://github.com/MomsFriendlyRobotCompany/thundercougarfalconbird/blob/main/pyproject.toml\n',
    'author': 'walchko',
    'author_email': 'walchko@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/thundercougarfalconbird/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
