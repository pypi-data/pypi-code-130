# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deap_er',
 'deap_er.algorithms',
 'deap_er.base',
 'deap_er.benchmarks',
 'deap_er.controllers',
 'deap_er.creator',
 'deap_er.gp',
 'deap_er.operators',
 'deap_er.operators.selection',
 'deap_er.records',
 'deap_er.strategies',
 'deap_er.utilities',
 'deap_er.utilities.hypervolume',
 'deap_er.utilities.sorting']

package_data = \
{'': ['*']}

install_requires = \
['dill>=0.3.5,<0.4.0', 'numpy>=1.23.1,<2.0.0', 'scipy>=1.8.1,<2.0.0']

setup_kwargs = {
    'name': 'deap-er',
    'version': '2.0.0',
    'description': 'Distributed Evolutionary Algorithms in Python - Entirely Reworked',
    'long_description': '# DEAP-ER\n\nDEAP-ER is a complete rework and refactor of the original DEAP evolutionary \ncomputation framework library for Python 3.9, 3.10 and up.\nIt seeks to make algorithms explicit and data structures transparent. \nIt works in perfect harmony with parallelization mechanisms such as \nmultiprocessing and [Ray](https://github.com/ray-project/ray).\n\nDEAP includes the following features:\n\n  * Genetic algorithm using any imaginable representation\n    * List, Array, Set, Dictionary, Tree, Numpy Array, etc.\n  * Genetic programming using prefix trees\n    * Loosely typed, Strongly typed\n    * Automatically defined functions\n  * Evolution strategies (including CMA-ES)\n  * Multi-objective optimisation (NSGA-II, NSGA-III, SPEA2, MO-CMA-ES)\n  * Co-evolution (cooperative and competitive) of multiple populations\n  * Parallelization of the evaluations (and more)\n  * Hall of Fame of the best individuals that lived in the population\n  * Checkpoints that take snapshots of a system regularly\n  * Benchmarks module containing most common test functions\n  * Genealogy of an evolution, that is also compatible with [NetworkX](https://github.com/networkx/networkx)\n  * Examples of alternative algorithms : Particle Swarm Optimization, Differential Evolution, Estimation of Distribution Algorithm\n\n## Documentation\n\nSee the [Documentation](http://deap-er.readthedocs.org/) for the user guide, tutorials and the reference manual.\n\n\n## Installation\n```bash\npip install deap-er\n```\n\n\n## Importing\n```python\nfrom deap_er import base, creator, tools, env, gp\n```\n\n\n## Contributing\n\nPlease read the CONTRIBUTING.md file before submitting pull requests.\n',
    'author': 'Mattias Aabmets',
    'author_email': 'mattias.aabmets@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
