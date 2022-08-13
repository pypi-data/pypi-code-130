# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openapi_python_client',
 'openapi_python_client.parser',
 'openapi_python_client.parser.properties',
 'openapi_python_client.schema',
 'openapi_python_client.schema.openapi_schema_pydantic']

package_data = \
{'': ['*'],
 'openapi_python_client': ['templates/*', 'templates/property_templates/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'attrs>=21.3.0',
 'autoflake>=1.4,<2.0',
 'black',
 'httpx>=0.15.4,<0.24.0',
 'isort>=5.0.5,<6.0.0',
 'jinja2>=3.0.0,<4.0.0',
 'pydantic>=1.6.1,<2.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'shellingham>=1.3.2,<2.0.0',
 'typer>=0.6,<0.7']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>2,<5', 'typing-extensions'],
 ':sys_platform == "win32"': ['colorama>=0.4.3,<0.5.0']}

entry_points = \
{'console_scripts': ['openapi-python-client = openapi_python_client.cli:app']}

setup_kwargs = {
    'name': 'openapi-python-client',
    'version': '0.11.5',
    'description': 'Generate modern Python clients from OpenAPI',
    'long_description': '![Run Checks](https://github.com/openapi-generators/openapi-python-client/workflows/Run%20Checks/badge.svg)\n[![codecov](https://codecov.io/gh/openapi-generators/openapi-python-client/branch/main/graph/badge.svg)](https://codecov.io/gh/triaxtec/openapi-python-client)\n[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)\n[![Generic badge](https://img.shields.io/badge/type_checked-mypy-informational.svg)](https://mypy.readthedocs.io/en/stable/introduction.html)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![PyPI version shields.io](https://img.shields.io/pypi/v/openapi-python-client.svg)](https://pypi.python.org/pypi/openapi-python-client/)\n[![Downloads](https://static.pepy.tech/personalized-badge/openapi-python-client?period=total&units=international_system&left_color=blue&right_color=green&left_text=Downloads)](https://pepy.tech/project/openapi-python-client)\n\n# openapi-python-client\n\nGenerate modern Python clients from OpenAPI 3.x documents.\n\n_This generator does not support OpenAPI 2.x FKA Swagger. If you need to use an older document, try upgrading it to\nversion 3 first with one of many available converters._\n\n**This project is still in development and does not support all OpenAPI features**\n\n## Why This?\n\nThis tool focuses on creating the best developer experience for Python developers by:\n\n1. Using all the latest and greatest Python features like type annotations and dataclasses.\n2. Having documentation and usage instructions specific to this one generator.\n1. Being written in Python with Jinja2 templates, making it easier to improve and extend for Python developers. It\'s also much easier to install and use if you already have Python.\n\n## Installation\n\nI recommend you install with [pipx](https://pipxproject.github.io/pipx/) so you don\'t conflict with any other packages you might have: `pipx install openapi-python-client --include-deps`.\n\n> Note the `--include-deps` option which will also make `black`, `isort`, and `autoflake` available in your path so that `openapi-python-client` can use them to clean up the generated code.\n\n**If you use `pipx run` then the post-generation hooks will not be available unless you install them manually.**\n\nYou can also install with normal pip: `pip install openapi-python-client`\n\nThen, if you want tab completion: `openapi-python-client --install-completion`\n\n## Usage\n\n### Create a new client\n\n`openapi-python-client generate --url https://my.api.com/openapi.json`\n\nThis will generate a new client library named based on the title in your OpenAPI spec. For example, if the title\nof your API is "My API", the expected output will be "my-api-client". If a folder already exists by that name, you\'ll\nget an error.\n\nIf you have an `openapi.json` file available on disk, in any CLI invocation you can build off that instead by replacing `--url` with a `--path`:\n\n`openapi-python-client generate --path location/on/disk/openapi.json`\n\n### Update an existing client\n\n`openapi-python-client update --url https://my.api.com/openapi.json`\n\n> For more usage details run `openapi-python-client --help` or read [usage](usage.md)\n\n### Using custom templates\n\nThis feature leverages Jinja2\'s [ChoiceLoader](https://jinja.palletsprojects.com/en/2.11.x/api/#jinja2.ChoiceLoader) and [FileSystemLoader](https://jinja.palletsprojects.com/en/2.11.x/api/#jinja2.FileSystemLoader). This means you do _not_ need to customize every template. Simply copy the template(s) you want to customize from [the default template directory](openapi_python_client/templates) to your own custom template directory (file names _must_ match exactly) and pass the template directory through the `custom-template-path` flag to the `generate` and `update` commands. For instance,\n\n```\nopenapi-python-client update \\\n  --url https://my.api.com/openapi.json \\\n  --custom-template-path=relative/path/to/mytemplates\n```\n\n_Be forewarned, this is a beta-level feature in the sense that the API exposed in the templates is undocumented and unstable._\n\n## What You Get\n\n1. A `pyproject.toml` file with some basic metadata intended to be used with [Poetry].\n1. A `README.md` you\'ll most definitely need to update with your project\'s details\n1. A Python module named just like the auto-generated project name (e.g. "my_api_client") which contains:\n   1. A `client` module which will have both a `Client` class and an `AuthenticatedClient` class. You\'ll need these\n      for calling the functions in the `api` module.\n   1. An `api` module which will contain one module for each tag in your OpenAPI spec, as well as a `default` module\n      for endpoints without a tag. Each of these modules in turn contains one function for calling each endpoint.\n   1. A `models` module which has all the classes defined by the various schemas in your OpenAPI spec\n\nFor a full example you can look at the `end_to_end_tests` directory which has an `openapi.json` file.\n"golden-record" in that same directory is the generated client from that OpenAPI document.\n\n## OpenAPI features supported\n\n1. All HTTP Methods\n1. JSON and form bodies, path and query parameters\n1. File uploads with multipart/form-data bodies\n1. float, string, int, date, datetime, string enums, and custom schemas or lists containing any of those\n1. html/text or application/json responses containing any of the previous types\n1. Bearer token security\n\n## Configuration\n\nYou can pass a YAML (or JSON) file to openapi-python-client with the `--config` option in order to change some behavior.\nThe following parameters are supported:\n\n### class_overrides\n\nUsed to change the name of generated model classes. This param should be a mapping of existing class name\n(usually a key in the "schemas" section of your OpenAPI document) to class_name and module_name. As an example, if the\nname of the a model in OpenAPI (and therefore the generated class name) was something like "\\_PrivateInternalLongName"\nand you want the generated client\'s model to be called "ShortName" in a module called "short_name" you could do this:\n\nExample:\n\n```yaml\nclass_overrides:\n  _PrivateInternalLongName:\n    class_name: ShortName\n    module_name: short_name\n```\n\nThe easiest way to find what needs to be overridden is probably to generate your client and go look at everything in the models folder.\n\n### project_name_override and package_name_override\n\nUsed to change the name of generated client library project/package. If the project name is changed but an override for the package name\nisn\'t provided, the package name will be converted from the project name using the standard convention (replacing `-`\'s with `_`\'s).\n\nExample:\n\n```yaml\nproject_name_override: my-special-project-name\npackage_name_override: my_extra_special_package_name\n```\n\n### field_prefix\n\nWhen generating properties, the `name` attribute of the OpenAPI schema will be used. When the `name` is not a valid\nPython identifier (e.g. begins with a number) this string will be prepended. Defaults to "field\\_".\n\nExample:\n\n```yaml\nfield_prefix: attr_\n```\n\n### package_version_override\n\nSpecify the package version of the generated client. If unset, the client will use the version of the OpenAPI spec.\n\nExample:\n\n```yaml\npackage_version_override: 1.2.3\n```\n\n### post_hooks\n\nIn the config file, there\'s an easy way to tell `openapi-python-client` to run additional commands after generation. Here\'s an example showing the default commands that will run if you don\'t override them in config:\n\n```yaml\npost_hooks:\n   - "autoflake -i -r --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports ."\n   - "isort ."\n   - "black ."\n```\n\n[changelog.md]: CHANGELOG.md\n[poetry]: https://python-poetry.org/\n',
    'author': 'Dylan Anthony',
    'author_email': 'danthony@triaxtec.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/triaxtec/openapi-python-client',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
