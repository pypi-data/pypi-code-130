# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['docstrings']

package_data = \
{'': ['*']}

install_requires = \
['docstring-parser>=0.14.1,<0.15.0', 'hikari-crescent>=0.3.0,<0.4.0']

setup_kwargs = {
    'name': 'crescent-ext-docstrings',
    'version': '0.2.0',
    'description': 'A docstring parser for hikari-crescent.',
    'long_description': '# crescent-ext-docstrings\n\nA docstring parser for [hikari-crescent](https://github.com/magpie-dev/hikari-crescent).\n\n## Installation\n```\npip install crescent-ext-docstrings\n```\n\n## Usage\n\nThis extension works for both class commands and function commands.\n\n```python\nimport crescent\nfrom crescent.ext import docstrings\n\nbot = crescent.Bot("...")\n\n@bot.include\n@docstrings.parse_doc\n@crescent.command\nasync def example(ctx: crescent.Context, a: str, b: str) -> None:\n    """\n    This is the command\'s description.\n    \n    :param a:\n        This is the first param\'s description.\n    :param b:\n        This is the first param\'s description.\n    """\n    await ctx.respond(f"{a=},{b=}")\n\n@bot.include\n@docstrings.parse_doc\n@crescent.command(name="class_example")\nclass ClassExample:\n    """\n    Other doc styles are supported. This is google doc style.\n    \n    Args:\n        a: This is the first param\'s description.\n        b: This is the first param\'s description.\n    """\n\n    a = crescent.option(str)\n    b = crescent.option(str)\n\n    async def callback(self, ctx: crescent.Context) -> None:\n        await ctx.respond(f"{self.a=},{self.b=}")\n\nbot.run()\n\n```\n\n### Doc Styles\nSince this library relies on [docstring-parser](https://github.com/rr-/docstring_parser), the styles Rest, Google, Numpy, and Epydoc are supported. If no style is specified, the style will be inferred.\n\n```python\nimport docstrings\n\n@bot.include\n@docstrings.parse_doc(style=docstrings.Style.REST)\n@crescent.command\nasync def example(ctx: crescent.Command, a: str) -> None:\n    """\n    Rest style description.\n\n    :param a:\n        The parameter.\n    """\n    ...\n\n```\n',
    'author': 'Lunarmagpie',
    'author_email': 'Bambolambo0@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
