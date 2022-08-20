# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clairvoyance', 'clairvoyance.entities']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp[speedups]>=3.8.1,<4.0.0', 'asyncio>=3.4.3,<4.0.0']

entry_points = \
{'console_scripts': ['clairvoyance = clairvoyance:cli']}

setup_kwargs = {
    'name': 'clairvoyance',
    'version': '2.0.1',
    'description': 'Obtain GraphQL API Schema even if the introspection is not enabled',
    'long_description': "# clairvoyance\n\nSome GraphQL APIs have disabled introspection. For example, [Apollo Server disables introspection automatically if the `NODE_ENV` environment variable is set to `production`](https://www.apollographql.com/docs/tutorial/schema/#explore-your-schema).\n\nClairvoyance allows us to get GraphQL API schema when introspection is disabled. It produces schema in JSON format suitable for other tools like [GraphQL Voyager](https://github.com/APIs-guru/graphql-voyager), [InQL](https://github.com/doyensec/inql) or [graphql-path-enum](https://gitlab.com/dee-see/graphql-path-enum).\n\n## Acknowledgments\n\nThanks to [Swan](https://github.com/c3b5aw) from [Escape-Technologies](https://github.com/Escape-Technologies) for 2.0 version.\n\n## Usage\n\n### From Python interpreter\n\n```bash\ngit clone https://github.com/nikitastupin/clairvoyance.git\ncd clairvoyance\npip install poetry\npoetry config virtualenvs.in-project true\npoetry install --no-dev\nsource .venv/bin/activate\n```\n\n```bash\npython3 -m clairvoyance --help\n```\n\n```bash\npython3 -m clairvoyance -o /path/to/schema.json https://swapi-graphql.netlify.app/.netlify/functions/index\n```\n\n### From Docker Image\n\n```bash\ndocker run --rm nikitastupin/clairvoyance --help\n```\n\n```bash\n# Assuming the wordlist.txt file is found in $PWD\ndocker run --rm -v $(pwd):/tmp/ nikitastupin/clairvoyance -vv -o /tmp/schema.json -w /tmp/wordlist.txt https://swapi-graphql.netlify.app/.netlify/functions/index\n```\n\nYou can refer to 2nd half of [GraphQL APIs from bug hunter's perspective by Nikita Stupin](https://youtu.be/nPB8o0cSnvM) talk for detailed description.\n\n### Which wordlist should I use?\n\nThere are at least two approaches:\n\n- Use general English words (e.g. [google-10000-english](https://github.com/first20hours/google-10000-english)).\n- Create target specific wordlist by extracting all valid GraphQL names from application HTTP traffic, from mobile application static files, etc. Regex for GraphQL name is [`[_A-Za-z][_0-9A-Za-z]*`](http://spec.graphql.org/June2018/#sec-Names).\n\n### Environment Variables\n\n```bash\nLOG_FMT=`%(asctime)s \\t%(levelname)s\\t| %(message)s` # A string format for logging.\nLOG_DATEFMT=`%Y-%m-%d %H:%M:%S` # A string format for logging date.\nLOG_LEVEL=`INFO` # A string level for logging.\n```\n\n## Support\n\nIn case of question or issue with clairvoyance please refer to [wiki](https://github.com/nikitastupin/clairvoyance/wiki) or [issues](https://github.com/nikitastupin/clairvoyance/issues). If this doesn't solve your problem feel free to open a [new issue](https://github.com/nikitastupin/clairvoyance/issues/new).\n\n## Contributing\n\nPull requests are welcome! For major changes, please open an issue first to discuss what you would like to change. For more information about tests, internal project structure and so on refer to [Development](https://github.com/nikitastupin/clairvoyance/wiki/Development) wiki page.\n",
    'author': 'Nikita Stupin',
    'author_email': 'nikitastupin@protonmail.com',
    'maintainer': 'Nikita Stupin',
    'maintainer_email': 'nikitastupin@protonmail.com',
    'url': 'https://github.com/nikitastupin/clairvoyance',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<=3.11',
}


setup(**setup_kwargs)
