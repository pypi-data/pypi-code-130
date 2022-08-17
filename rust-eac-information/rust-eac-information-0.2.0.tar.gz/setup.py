# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['eac_info']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'beautifulsoup4>=4.11.1,<5.0.0', 'lxml>=4.9.1,<5.0.0']

setup_kwargs = {
    'name': 'rust-eac-information',
    'version': '0.2.0',
    'description': 'Get infromation about eac banned players in rust',
    'long_description': '# Rust EAC Information \n## Install \n```\npip install rust-eac-information\n```\n\n## How to use?\nAsync method\n```python\nfrom eac_info import get_eac_info\n\n\nasync def foo():\n    return await get_eac_info(76561198256263906)\n\neac = foo()\n```\n\nSync method\n```python\nimport asyncio\n\nfrom eac_info import get_eac_info\n\neac = asyncio.get_event_loop().run_until_complete(get_eac_info(76561198256263906))\n```\n\nPropertys\n```python\neac.steamid  # 76561198256263906\neac.is_ban  # True\neac.ban_time  # datetime.datetime(2022, 7, 22, 0, 0)\neac.days_since_ban  # 26\neac.post_link  # https://twitter.com/rusthackreport/status/1550304891448557569?ref_src=twsrc%5Etfw\neac.nexus_link  # https://www.nexusonline.co.uk/bans/profile/?id=76561198256263906\n```\n\n# About\nThis script works with [nexus](https://www.nexusonline.co.uk/bans/) and simply converts the information into python objects. If the site does not work, then the script will stop functioning.\n\nThe author has nothing to do with the [nexus](https://www.nexusonline.co.uk)\n\n',
    'author': 'MaHryCT3',
    'author_email': 'mahryct123@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MaHryCT3/rust-eac-infromation',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
