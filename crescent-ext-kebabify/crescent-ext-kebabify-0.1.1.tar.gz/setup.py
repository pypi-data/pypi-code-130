# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kebab']

package_data = \
{'': ['*']}

install_requires = \
['hikari-crescent>=0.3.0,<0.4.0']

setup_kwargs = {
    'name': 'crescent-ext-kebabify',
    'version': '0.1.1',
    'description': 'Turn your command names into kebabs.',
    'long_description': '# crescent-ext-kebabify\n\nTurn your command names into kebabs.\n\n\n## Installing\n`pip install crescent-ext-kebabify`\n\n\n## Example\n\n```python\n\nimport crescent\nfrom crescent.ext import kebab\n\nbot = crescent.Bot("TOKEN")\n\n\n# Make this command\'s name `my-class-command`\n@bot.include\n@kebab.ify\n@crescent.command\nclass MyClassCommand:\n    async def callback(self, ctx: crescent.Context):\n        ...\n\n\n# Make this command\'s name `my-function-command`\n@bot.include\n@kebab.ify\n@crescent.command\nasync def my_function_commannd(ctx: crescent.Context):\n    ...\n\nbot.run()\n\n```\n',
    'author': 'Lunarmagpie',
    'author_email': 'Bambolambo0@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Lunarmagpie/crescent-ext-kebabify',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
