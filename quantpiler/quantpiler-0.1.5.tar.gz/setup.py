# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quantpiler']

package_data = \
{'': ['*']}

install_requires = \
['qiskit>=0.37.1,<0.38.0']

setup_kwargs = {
    'name': 'quantpiler',
    'version': '0.1.5',
    'description': 'Quantum compiler and common circuits generator',
    'long_description': '[![License](https://img.shields.io/github/license/averyanalex/quantpiler.svg?)](https://opensource.org/licenses/Apache-2.0)\n[![Publish status](https://github.com/averyanalex/quantpiler/actions/workflows/publish.yml/badge.svg)](https://github.com/averyanalex/quantpiler/actions/workflows/publish.yml)\n[![Latest release](https://img.shields.io/github/tag/averyanalex/quantpiler.svg)](https://github.com/averyanalex/quantpiler/tags)\n[![Downloads](https://pepy.tech/badge/quantpiler)](https://pypi.org/project/quantpiler/)\n\n# Quantpiler\n\nThis library can generate some common circuits and compile python functions to circuits\n\n## Examples:\n\n### Compile:\n\n```python\nfrom quantpiler.compiler import compile\n\ndef example_func(a, b):\n    a = True\n    a_or_b = a | b\n    tmp = a & (a_or_b | (a == b))\n    b = tmp != False\n\nqc = compile(example_func, 4)\nqc.draw(output="mpl")\n```\n\n![Compiled circuit](https://raw.githubusercontent.com/averyanalex/quantpiler/397073274ea07ad9d3f85345cf15823ed79813f0/images/compiler.png)\n\n### qRAM\n\n```python\nfrom quantpiler.qram import new_qram\n\nvalues = {0: 1, 1: 3, 2: 6, 3: 7}\nqram = new_qram(2, 3, values)\n\nqram.draw(output="mpl")\n```\n\n![qRAM circuit](https://raw.githubusercontent.com/averyanalex/quantpiler/397073274ea07ad9d3f85345cf15823ed79813f0/images/qram.png)\n',
    'author': 'AveryanAlex',
    'author_email': 'alex@averyan.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/averyanalex/quantpiler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
