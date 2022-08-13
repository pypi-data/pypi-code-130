# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydantic_partial']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'pydantic-partial',
    'version': '0.2.1',
    'description': 'Create partial models from your pydantic models. Partial models may allow None for certain or all fields.',
    'long_description': '# pydantic-partial\n\nCreate partial models from your normal pydantic models. Partial models will allow\nsome or all fields to be optional and thus not be required when creating the model\ninstance.\n\nPartial models can be used to support PATCH HTTP requests where the suer only wants\nto update some fields of the model and normal validation for required fields is not\nrequired. It may also be used to have partial response DTO\'s where you want to skip\ncertain fields, this can be useful in combination with `exclude_none`. It is - like\nshown in these examples - intended to be used with API use cases, so when using\npydantic with for example FastAPI.\n\n**Disclaimer:** This is the first public release of pydantic-partial. Things might\nchange in the future.\n\n# Usage example\n\npydantic-partial provides a mixin to generate partial model classes. The mixin can\nbe used like this:\n\n```python\n# Something model, than can be used as a partial, too:\nclass Something(PartialModelMixin, pydantic.BaseModel):\n    name: str\n    age: int\n\n\n# Create a full partial model\nFullSomethingPartial = Something.as_partial()\nFullSomethingPartial(name=None, age=None)\n# You could also create a "partial Partial":\n#AgeSomethingPartial = Something.as_partial("age")\n```\n',
    'author': 'TEAM23 GmbH',
    'author_email': 'info@team23.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/team23/pydantic-partial',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
