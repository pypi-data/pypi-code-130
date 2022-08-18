# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['glimix_core',
 'glimix_core._ep',
 'glimix_core._util',
 'glimix_core._util.test',
 'glimix_core.cov',
 'glimix_core.cov.test',
 'glimix_core.example',
 'glimix_core.ggp',
 'glimix_core.ggp.test',
 'glimix_core.glmm',
 'glimix_core.glmm.test',
 'glimix_core.gp',
 'glimix_core.gp.test',
 'glimix_core.lik',
 'glimix_core.lik.test',
 'glimix_core.link',
 'glimix_core.link.test',
 'glimix_core.lmm',
 'glimix_core.lmm.test',
 'glimix_core.mean',
 'glimix_core.mean.test',
 'glimix_core.mt',
 'glimix_core.random',
 'glimix_core.random.test']

package_data = \
{'': ['*']}

install_requires = \
['brent-search',
 'liknorm>=1.2.8',
 'ndarray-listener',
 'numpy',
 'numpy-sugar',
 'optimix',
 'pytest',
 'pytest-doctestplus',
 'scipy',
 'tqdm']

setup_kwargs = {
    'name': 'glimix-core',
    'version': '3.1.13',
    'description': 'Fast inference over mean and covariance parameters for Generalised Linear Mixed Models',
    'long_description': '# glimix-core\n\n[![Documentation](https://readthedocs.org/projects/glimix-core/badge/?version=latest)](https://glimix-core.readthedocs.io/en/latest/?badge=latest)\n\nFast inference over mean and covariance parameters for Generalised Linear Mixed\nModels.\n\nIt implements the mathematical tricks of\n[FaST-LMM](https://github.com/MicrosoftGenomics/FaST-LMM) for the special case\nof Linear Mixed Models with a linear covariance matrix and provides an\ninterface to perform inference over millions of covariates in seconds.\nThe Generalised Linear Mixed Model inference is implemented via Expectation\nPropagation and also makes use of several mathematical tricks to handle large\ndata sets with thousands of samples and millions of covariates.\n\n## Install\n\nThere are two main ways of installing it.\nVia [pip](https://pypi.python.org/pypi/pip):\n\n```bash\npip install glimix-core\n```\n\nOr via [conda](http://conda.pydata.org/docs/index.html):\n\n```bash\nconda install -c conda-forge glimix-core\n```\n\n## Running the tests\n\nAfter installation, you can test it\n\n```bash\npython -c "import glimix_core; glimix_core.test()"\n```\n\nas long as you have [pytest](https://docs.pytest.org/en/latest/).\n\n## Usage\n\nHere it is a very simple example to get you started:\n\n```python\n>>> from numpy import array, ones\n>>> from numpy_sugar.linalg import economic_qs_linear\n>>> from glimix_core.lmm import LMM\n>>>\n>>> X = array([[1, 2], [3, -1], [1.1, 0.5], [0.5, -0.4]], float)\n>>> QS = economic_qs_linear(X, False)\n>>> X = ones((4, 1))\n>>> y = array([-1, 2, 0.3, 0.5])\n>>> lmm = LMM(y, X, QS)\n>>> lmm.fit(verbose=False)\n>>> lmm.lml()\n-2.2726234086180557\n```\n\nWe  also provide an extensive [documentation](http://glimix-core.readthedocs.org/) about the library.\n\n## Authors\n\n* [Danilo Horta](https://github.com/horta)\n\n## License\n\nThis project is licensed under the [MIT License](https://raw.githubusercontent.com/limix/glimix-core/master/LICENSE.md).\n',
    'author': 'Danilo Horta',
    'author_email': 'danilo.horta@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/limix/glimix-core',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
