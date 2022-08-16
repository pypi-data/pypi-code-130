# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['paradigm_panes']

package_data = \
{'': ['*']}

install_requires = \
['hfst-optimized-lookup>=0.0.13,<0.1.0',
 'more-itertools>=8.7.0,<8.8.0',
 'typing-extensions>=3.7,<4.0']

setup_kwargs = {
    'name': 'paradigm-panes',
    'version': '0.3.4',
    'description': 'Paradigm panes meant to provide layout specification to be reused elsewhere.',
    'long_description': '# paradigm-panes\n\nInstallable package that produces a paradigm for a given word, given a pointer to paradigm layouts and FST file. Originally\nbuilt for [itwêwina](https://itwewina.altlab.app/).\n\n# PyPi Package\n\nLatest version of the package posted to PyPi: [paradigm-panes 0.3.2](https://pypi.org/project/paradigm-panes/)\n\n# Install\n\n```\npip install paradigm-panes\n```\n\n# Developing\n\nDeveloping is done and managed through [Python Poetry](https://python-poetry.org/) package manager.\n\nTo start development:\n\n```\n# Download the repo\ngit clone https://github.com/UAlbertaALTLab/paradigm-panes.git\n\n# Set up virutal env\nvirtualenv venv --python=python3.9\nsource venv/bin/activate\n\n# Install dependencies\npoetry install\n\n# Now cd into main directory and try out the package\ncd paradigm_panes\npython\n    >>> import paradigm_panes\n    >>> ...\n```\n\n# API Documentation:\n\n- ## PaneGenerator()\n\n  For successful execution, the package needs a link to resources as described below. To manage different links and use the panes generator more effectively, the package provides PaneGenerator class that allows managing settings and executing main functionality:\n\n  ```\n  >>> pane_generator = paradigm_panes.PaneGenerator()\n  ```\n\n  The class itself does not take any variables.\n\n- ## generate_pane()\n\n  ```\n  >>> paradigm = pane_generator.generate_pane(lemma, paradigm_type, size: Optional)\n  ```\n\n  This function is a core functionality of the package. Once the [resources are specified](#settings-specification-functions), this function generates the pane according to the specification given. \\\n   If the translations are not found in the FST file, some of the inflections will be indicated as missing. The resulted paradigm class is serialized and returned as JSON.\n\n  ### Parameters:\n\n  > lemma(str) - base wordform to be inflected\n\n  > paradigm_type(str) - specification of the paradigm type of the word. Ex. "NA".\n\n  > size(str) - optional size of the pane to be returned. Currently supports "base", and "full". If the specified size is not found, overrides with default option.\n\n- ## all_analysis_template_tags()\n\n  ```\n  >>> paradigm = pane_generator.all_analysis_template_tags(paradigm_type)\n  ```\n\n  An additional functionality that returns all analysis template tags.\n\n  ### Parameters:\n\n  > paradigm_type(str) - specification of the paradigm type of the word. Ex. "NA".\n\n  > tag_style(str) - style of tags to return.\n\n  Specify tag style through [settings](#settings-specification-functions)\n\n# Usage and Configuration\n\nImport the library:\n\n```\n>>> import paradigm_panes\n```\n\nCreate PaneGenerator and specify path to FST file and layouts resources:\n\n```\n>>> pg = paradigm_panes.PaneGenerator()\n>>> pg.set_layouts_dir("/home/ubuntu/paradigm_panes/resources/layouts")\n>>> pg.set_fst_filepath("/home/ubuntu/paradigm_panes/resources/fst/crk-strict-generator.hfstol")\n```\n\nPass lemma, paradigm type, and optional size to generate a pane:\n\n```\n>>> lemma = "amisk"\n>>> p_type = "NA"\n>>> paradigm = pg.generate_pane(lemma, p_type)\n\n>>> p_size = "full"\n>>> full_paradigm = pg.generate_pane(lemma, p_type, p_size)\n```\n\n## Settings specification functions:\n\n- `set_layouts_dir(path)` specifies a location of a directory with paradigm layouts that are relevant for current paradigm generation.\n\n- `set_fst_filepath(path)` specifies FST file location with layout translation that are relevant for current paradigm generation.\n\n- `set_tag_style(path)` specifies template rendering type for all_analysis_template_tags function.\n\n  Available tag styles:\n\n  1.  "Plus"\n  2.  "Bracket"\n\nThe generator must specify both locations (FST, layouts) before generating a paradigm.\n\nSize is optional to paradigm generation; by default a base size (or first available) will be used.\n\n# Testing\n\nTo run the tests you need to install required dependencies, it is easier by using a virtual environment like this:\n\n```\n>>> # Set up virutal env\n>>> virtualenv venv --python=python3.9\n>>> source venv/bin/activate\n>>>\n>>> # Install dependencies\n>>> poetry install\n```\n\nOnce the dependencies are installed you can run tests by calling pytest.\n\n```\n>>> pytest\n```\n\n# Release\n\nPackage version number is sorted in pyproject.toml. With every release to PyPi the version needs to be updated. \\\nBuild the package from the main directory before publishing it:\n\n```\n>>> poetry build\n```\n\nTo publish to Test PyPi use poetry and enter credentials associated with Test PyPi account\n\n```\n>>> poetry publish -r testpypi\n```\n\nTo publish to real PyPi use poetry and enter credentials associated with PyPi\n\n```\n>>> poetry publish\n```\n\nAll relevant package specifications and dependencies are managed in `pyproject.toml` file.\n',
    'author': 'Uladzimir Bondarau',
    'author_email': 'bondarau@ualberta.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UAlbertaALTLab/paradigm-panes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
