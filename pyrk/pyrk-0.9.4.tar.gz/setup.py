# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyrk']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyrk',
    'version': '0.9.4',
    'description': 'ode integration rk4 rk runge kutta',
    'long_description': '![Header pic](https://github.com/walchko/pyrk/raw/master/pics/math2.jpg)\n\n# Runge-Kutta\n\n[![Actions Status](https://github.com/walchko/pyrk/workflows/pytest/badge.svg)](https://github.com/walchko/pyrk/actions)\n![PyPI - License](https://img.shields.io/pypi/l/pyrk.svg)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyrk.svg)\n![PyPI - Format](https://img.shields.io/pypi/format/pyrk.svg)\n![PyPI](https://img.shields.io/pypi/v/pyrk.svg)\n\nA simple implementation of\n[Runge-Kutta](https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods)\nfor python.\n\n## Usage\n\nIntegrates a function x_dot = f(time, x, u). See the examples in the\n[docs](https://github.com/walchko/pyrk/blob/master/doc/runge-kutta.ipynb)\nfolder or a simple one:\n\n``` python\nfrom pyrk import RK4\nimport numpy as np\nimport matplotlib.pyplot as plt\n\ndef vanderpol(t, xi, u):\n    dx, x = xi\n    mu = 4.0 # damping\n\n    ddx = mu*(1-x**2)*dx-x\n    dx = dx\n\n    return np.array([ddx, dx])\n\nrk = RK4(vanderpol)\nt, y = rk.solve(np.array([0, 1]), .01, 200)\n\ny1 = []\ny2 = []\nfor v in y:\n    y1.append(v[0])\n    y2.append(v[1])\n\nplt.plot(y1, y2)\nplt.ylabel(\'velocity\')\nplt.xlabel(\'position\')\nplt.grid(True)\nplt.show()\n```\n\n## Alternative\n\nIf you want to use `scipy` (which is good, but big), you can do:\n\n```python\nfrom scipy.integrate import solve_ivp rk45\n\ndef func(t,x,u):\n    # cool differential equations\n    # ...\n    return x\n\nt = 0\ndt = 0.01\ny = np.array([0,0,0]) # initial state\n\nfor _ in tqdm(range(steps)):\n    u = np.array([1,2,3]) # some inputs to func (i.e., control effort)\n\n    y = rk45(func, [t, t+step], y, args=(u,))\n\n    if y.success == False:\n        print("Oops")\n\n    y = y.y[:,-1]\n\n    # probably save t, u and y into arrays for plotting\n    t += step\n```\n\n# MIT License\n\n**Copyright (c) 2015 Kevin J. Walchko**\n\nPermission is hereby granted, free of charge, to any person obtaining a\ncopy of this software and associated documentation files (the\n"Software"), to deal in the Software without restriction, including\nwithout limitation the rights to use, copy, modify, merge, publish,\ndistribute, sublicense, and/or sell copies of the Software, and to\npermit persons to whom the Software is furnished to do so, subject to\nthe following conditions:\n\nThe above copyright notice and this permission notice shall be included\nin all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS\nOR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF\nMERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.\nIN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY\nCLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,\nTORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE\nSOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n',
    'author': 'walchko',
    'author_email': 'walchko@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/pyrk/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
