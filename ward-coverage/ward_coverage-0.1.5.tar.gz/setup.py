# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ward_coverage']

package_data = \
{'': ['*']}

install_requires = \
['coverage>=6.0,<7.0', 'toml>=0.10.0,<0.11.0', 'ward>=0.66.0-beta.0,<0.67.0']

setup_kwargs = {
    'name': 'ward-coverage',
    'version': '0.1.5',
    'description': 'A coverage plugin for Ward testing framework',
    'long_description': '# Ward Coverage\n\n[![CI/CD](https://github.com/petereon/ward_coverage/actions/workflows/python-test.yml/badge.svg?branch=master)](https://github.com/petereon/ward_coverage/actions/workflows/python-test.yml) [![MyPy Lint](https://github.com/petereon/ward_coverage/actions/workflows/python-lint.yml/badge.svg?branch=master)](https://github.com/petereon/ward_coverage/actions/workflows/python-lint.yml) [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=petereon_ward_coverage&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=petereon_ward_coverage)\n\n__Disclaimer: Albeit useful already, this is a work-in-progress and should be seen as such.__ \n\nA coverage plugin for Python\'s [Ward testing framework](https://ward.readthedocs.io/en/latest/)\n\n![Example image](https://raw.githubusercontent.com/petereon/ward-coverage/master/resources/screen.png)\n\n## Installation\n\nBuild the plugin:\n\n```bash\npoetry build\n```\nand install using\n\n```bash\npip install dist/ward_coverage-0.1.1-py3-none-any.whl\n```\n\n## Configuration\n\nTo include coverage in your test run, add the following to your `pyproject.toml`:\n\n```toml\n[tool.ward]\nhook_module = ["ward_coverage"]\n```\n\nThere are several options to configure the plugin which can be included under section `[tool.ward.plugins.coverage]`, namely:\n- All the constructor parameters of `Coverage` class as described here: [https://coverage.readthedocs.io/en/6.4/api_coverage.html#coverage.Coverage](https://coverage.readthedocs.io/en/6.4/api_coverage.html#coverage.Coverage)\n- `report_type`, defaulting to `["term"]`, which is a list of report types to generate. Possible values are one or more of _\'lcov\'_, _\'html\'_, _\'xml\'_, _\'json\'_, _\'term\'_\n\n__Contributors, issues and feature requests are welcome.__\n',
    'author': 'Peter Vyboch',
    'author_email': 'pvyboch1@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/petereon/ward_coverage',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.8,<4.0.0',
}


setup(**setup_kwargs)
