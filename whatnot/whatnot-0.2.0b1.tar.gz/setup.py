# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['whatnot']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'gql>=3.3.0,<4.0.0']

setup_kwargs = {
    'name': 'whatnot',
    'version': '0.2.0b1',
    'description': 'An asynchronous, unofficial Whatnot API wrapper',
    'long_description': '# Whatnot API\n\nWork-in-progress unofficial asynchronous API wrapper for [Whatnot](https://www.whatnot.com) API.\n\n## Download\n\n`poetry add whatnot` *or* `pip install whatnot`\n\n## Roadmap\n\nSee [ROADMAP.md](ROADMAP.md)\n\n## Example\n\n```python\nimport asyncio\nfrom whatnot import Whatnot\n\nasync def main():\n    async with Whatnot() as whatnot:\n        whatnot.login("bob@example.com", "secret_password")\n\n        # Get the whatnot account\n        whatnot_user = await whatnot.get_user("whatnot")\n        print(whatnot_user.username)\n        # OR await whatnot.get_user_by_id("21123")\n\n        # Get user\'s lives\n        lives = await whatnot.get_user_lives(whatnot_user.id)\n\n        # Print out all of the lives\n        for live in lives:\n            print(live.title)\n\n\nasyncio.run(main())\n```\n\n## Disclaimer\n\nThis project is unofficial and is not affiliated with or endorsed by Whatnot.\n',
    'author': 'wxllow',
    'author_email': 'willow@wxllow.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wxllow/whatnot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
