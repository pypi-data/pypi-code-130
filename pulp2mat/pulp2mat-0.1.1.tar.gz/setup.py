# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pulp2mat']

package_data = \
{'': ['*']}

install_requires = \
['PuLP>=2.6.0,<3.0.0', 'numpy>=1.23.2,<2.0.0', 'scipy>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'pulp2mat',
    'version': '0.1.1',
    'description': 'convert pulp model into matrix formulation for scipy.optimize.milp',
    'long_description': '# pulp2mat\n\nConvert pulp model into matrix formulation.\n\nIt can be easily thrown to scipy.optimize.milp function.\n\n\n# How to install\n\n```\n$ pip install pulp2mat\n```\n\nWithout poetry, please look at pyproject.toml and install all dependencies manually. \n\n# Quick Example\n\nAll variables must be defined in dictionaries. The key is tuple of variable indices, the value is pulp.LpVariable.\n\nFor example, the binpacking problem can be formulated with pulp as below;\n\n```python\nimport pulp as pl\nimport numpy as np\n\nitem_sizes = np.array([7, 3, 3, 1, 6, 8, 4, 9, 5, 2])\nnum_items = len(item_sizes)\nnum_bins = len(item_sizes)\nbin_size = 10\n\n# Variables * must be defined as dictionaries\nx = {\n    (i, j): pl.LpVariable("x_{}_{}".format(i, j), cat=pl.LpBinary)\n    for i in range(num_items)\n    for j in range(num_bins)\n}\ny = {\n    j: pl.LpVariable("y_{}".format(j), cat=pl.LpBinary)\n    for j in range(num_bins)\n}\n\nproblem = pl.LpProblem()\n\n# Bin size constraint for each bin\nfor j in range(num_bins):\n    problem += (\n        pl.lpSum(\n            x[i, j] * item_sizes[i] for i in range(num_items)\n        )\n        <= bin_size * y[j]\n    )\n# One-hot constraint for each item\nfor i in range(num_items):\n    problem += pl.lpSum(x[i, j] for j in range(num_bins)) == 1\n\n# Objective: minimize number of bins used.\nproblem += pl.lpSum(y[j] for j in range(num_bins))\n```\n\nthe ```pulp.LpProblem``` object and the list of variable dictionaries can be converted to the matrix format for ```scipy.optimize.milp```.\n\n```python\nimport pulp2mat\nfrom scipy.optimize import milp\nc, integrality, constraints, bounds = pulp2mat.convert_all(problem, [x, y])\nresult = milp(c, integrality=integrality, constraints=constraints, bounds=bounds)\n```\n',
    'author': 'rtonoue',
    'author_email': 'rtonoue625@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rtonoue/pulp2mat',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
