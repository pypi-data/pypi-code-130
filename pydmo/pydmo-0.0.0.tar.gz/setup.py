# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydmo']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.4,<9.0.0',
 'datamodel-code-generator>=0.13.1,<0.14.0',
 'jupyter>=1.0.0,<2.0.0',
 'jupytext>=1.13.7,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'python-dotenv>=0.20.0,<0.21.0']

extras_require = \
{'docs': ['importlib-metadata>=4.11.3,<5.0.0',
          'myst-parser>=0.17.0,<0.18.0',
          'pygments>=2.11.2,<3.0.0',
          'sphinx>=4.4.0,<5.0.0',
          'sphinx-autodoc-typehints>=1.17.0,<2.0.0',
          'pydata-sphinx-theme>=0.8.0,<0.9.0',
          'sphinxcontrib-apidoc>=0.3.0,<0.4.0',
          'sphinx-click>=3.1.0,<4.0.0',
          'jinja2<3.1']}

entry_points = \
{'console_scripts': ['cli = bin.cli:cli']}

setup_kwargs = {
    'name': 'pydmo',
    'version': '0.0.0',
    'description': 'Pydmo: Build a database pydantic schema from its collection of data tables',
    'long_description': '# pydmo\n\n**Documentation**: [https://strayMat.gitlab.io/pydmo](https://strayMat.gitlab.io/pydmo)\n\n**Source Code**: [https://gitlab.com/strayMat/pydmo](https://gitlab.com/strayMat/pydmo)\n\nThis projects implements the creation of [pydantic] data models from a collection of dataset (eg. pandas dataset). \n\n\n## Motivation\n\nHaving typed data models in python files is very useful for :\n\n- Code testing thanks to dummy data generation\n- Data validation\n- Documentation generation\n\nThese usages are motivated by the blog post: [data templates with pydantic](https://ianwhitestone.work/data-templates-with-pydantic/)\n\n## Links with other projects\n\nThe [Table-schema-translator](https://framagit.org/interhop/library/table-schema-translator/-/tree/master) takes yaml as input to generate scala data models for spark.  \n\nWe use the [pydantic code generation package](https://koxudaxi.github.io/datamodel-code-generator/jsonschema/).\n\nThe python API should be installed with pip as [recommanded in the documentation](https://koxudaxi.github.io/datamodel-code-generator/using_as_module/). \n\n> 📝 **Note**\n> Use English for all content in this project\n\nMight be useful if we want to integrate some features existing only on table schema: [Pandas api for table schema](https://pandas.pydata.org/docs/reference/api/pandas.io.json.build_table_schema.html)\n---\n\n## Overview\n\n- TODO\n\n## Features\n\n- TODO\n',
    'author': 'Matthieu Doutreligne',
    'author_email': 'matt.dout@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/strayMat/pydmo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
