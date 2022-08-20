# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycomex', 'pycomex.examples', 'tests']

package_data = \
{'': ['*'], 'pycomex': ['templates/*']}

install_requires = \
['click==7.1.2', 'jinja2==3.0.3', 'matplotlib>=3.5.2', 'numpy>=1.22.0']

entry_points = \
{'console_scripts': ['pycomex = pycomex.cli:main']}

setup_kwargs = {
    'name': 'pycomex',
    'version': '0.3.1',
    'description': 'Python Computational Experiments',
    'long_description': '.. image:: https://img.shields.io/pypi/v/pycomex.svg\n        :target: https://pypi.python.org/pypi/pycomex\n\n.. image:: https://readthedocs.org/projects/pycomex/badge/?version=latest\n        :target: https://pycomex.readthedocs.io/en/latest/?version=latest\n        :alt: Documentation Status\n\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n\nPyComex - Python Computational Experiments\n================================================\n\nMicroframework to improve the experience of running and managing records of computational experiments,\nsuch as machine learning and data science experiments, in Python.\n\n* Free software: MIT license\n* Documentation: https://pycomex.readthedocs.io.\n\nFeatures\n--------\n\n* Automatically create (nested) folder structure for results of each run of an experiment\n* Simply attach metadata such as performance metrics to experiment object and they will be automatically\n  stored as JSON file\n* Easily attach file artifacts such as ``matplotlib`` figures to experiment records\n* Log messages to stdout as well as permanently store into log file\n\nInstallation\n------------\n\nInstall stable version with ``pip``\n\n.. code-block:: console\n\n    pip3 install pycomex\n\nOr the most recent development version\n\n.. code-block:: console\n\n    git clone https://github.com/the16thpythonist/pycomex.git\n    cd pycomex ; pip3 install .\n\nQuickstart\n----------\n\nEach computational experiment has to be bundled as a standalone python module. Important experiment\nparameters are placed at the top. Actual execution of the experiment is placed within the ``Experiment``\ncontext manager.\n\nUpon entering the context, a new storage folder for each run of the experiment is created.\n\nStorage of metadata, file artifacts and error handling is automatically managed on context exit.\n\n.. code-block:: python\n\n    """\n    This doc string will be saved as the "description" meta data of the experiment records\n    """\n    from pycomex.experiment import Experiment\n\n    # Experiment parameters can simply be defined as uppercase global variables.\n    # These are automatically detected and can possibly be overwritten in command\n    # line invocation\n    HELLO = \'hello \'\n    WORLD = \'world!\'\n\n    # Experiment context manager needs 3 positional arguments:\n    # - Path to an existing folder in which to store the results\n    # - A namespace name unique for each experiment\n    # - access to the local globals() dict\n    with Experiment(\'/tmp/results\', \'example\', globals()) as e:\n        e.prepare() # important!\n\n        # Internally saved into automatically created nested dict\n        # {\'strings\': {\'hello_world\': \'...\'}}\n        e[\'strings/hello_world\'] = HELLO + WORLD\n\n        # Alternative to "print". Message is printed to stdout as well as\n        # recorded to log file\n        e.info(\'some debug message\')\n\n        # Automatically saves text file artifact to the experiment record folder\n        file_name = \'hello_world.txt\'\n        e.commit_raw(file_name, HELLO + WORLD)\n        # e.commit_fig(file_name, fig)\n        # e.commit_png(file_name, image)\n        # ...\n\n\nThis example would create the following folder structure:\n\n.. code-block:: text\n\n    tmp\n    |- results\n       |- example\n          |- 000\n             |+ experiment_log.txt\n             |+ experiment_data.json\n             |+ hello_world.txt\n\nFor more information and more interesting examples visit the Documentation: https://pycomex.readthedocs.io !\n\nCredits\n-------\n\nThis package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.\n\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage\n',
    'author': 'Jonas Teufel',
    'author_email': 'jonseb1998@gmail.com',
    'maintainer': 'Jonas Teufel',
    'maintainer_email': 'jonseb1998@gmail.com',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2',
}


setup(**setup_kwargs)
