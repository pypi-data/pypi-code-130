# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spiceweasel']

package_data = \
{'': ['*']}

install_requires = \
['numpy', 'pyrk']

setup_kwargs = {
    'name': 'spiceweasel',
    'version': '0.0.3',
    'description': 'Kalman filter stuff',
    'long_description': '![](https://github.com/MomsFriendlyRobotCompany/spiceweasel/raw/main/pics/elzar.png)\n\n![GitHub](https://img.shields.io/github/license/MomsFriendlyRobotCompany/spiceweasel)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/spiceweasel)\n![PyPI](https://img.shields.io/pypi/v/spiceweasel)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/spiceweasel?color=aqua)\n\n# Spice Weasel\n\n>  I knocked it up a notch with my `spiceweasel`. Bam!\n\n**under development**\n\nThe list of imported packages can be found in the [pyproject.toml][toml].\n\n## Usage\n\nBasic example:\n\n```python\nimport numpy as np\nfrom spiceweasel import EKF\n\ndef func(dt, x, u):\n    """\n    dt: time step\n    x: state estimate\n    u: control forces or other inputs\n    """\n\n    # differential equations\n    return x\n\n# create a kalman filter\nekf = EKF(func, dt, 2, 2)\n\n# so reset puts R and Q to identify matrix, you should\n# adjust them to your system\nekf.reset()\nekf.R *= [0.01,0.01,0.1] # measurement cov\nekf.Q *= [.05,.05,.1]    # process cov\nekf.x = np.array([1,-2]) # default sets this to zeros\n\n# main filtering loop\nfor i in range(num):\n    # ...\n    ekf.predict(u)\n    # ...\n    y = ekf.update(meas)\n\n# ...\n```\n\n# MIT License\n\n**Copyright (c) 2022 Mom\'s Friendly Robot Company**\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n\n[toml]: https://github.com/MomsFriendlyRobotCompany/spiceweasel/blob/main/pyproject.toml\n',
    'author': 'walchko',
    'author_email': 'walchko@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/spiceweasel/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
