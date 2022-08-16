# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['dnfunc']
install_requires = \
['PyYAML>=6.0,<7.0',
 'VapourSynth>=59,<60',
 'havsfunc>=33,<34',
 'lvsfunc>=0.4.3,<0.5.0',
 'vsutil>=0.8.0,<0.9.0']

setup_kwargs = {
    'name': 'dnfunc',
    'version': '0.0.1a0',
    'description': 'A collection of Vapoursynth functions and wrapperspoetr',
    'long_description': '# dnfunc\n\n> A collection of Vapoursynth functions and wrappers\n\n[![pre-commit.ci](https://results.pre-commit.ci/badge/github/DeadNews/dnfunc/main.svg)](https://results.pre-commit.ci/latest/github/DeadNews/dnfunc/main)\n',
    'author': 'DeadNews',
    'author_email': 'uhjnnn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DeadNews/dnfunc',
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
