# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'lib'}

packages = \
['big_slpp']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'big-slpp',
    'version': '1.0.4',
    'description': "SirAnthony's SLPP, but modernized code (also, trailing comma's)",
    'long_description': '# Big-SLPP\n\nBig-SLPP is a simple lua-python data structures parser that also has trailing comma\'s.\n\nIt also has two helper functions to help me re-create the files, as created by WoW.\n\n## Example input\n\n```lua\n-- This is a lua file from the game World of Warcraft: Wrath of the Lich King\n-- I need those keys sorted, because WoW/Lua keeps moving around the keys for\n-- no good damn reason >:(\n-- HOW DO YOU EXPECT ME TO TRACK MY SETTINGS IN A REPO, BLIZZARD!?\n-- jk, I know Wrath is still relatively rough around the edges.\n\n_NPCScanOptionsCharacter = {\n\t["Achievements"] = {\n\t\t[1312] = true,\n\t\t[2257] = true,\n\t},\n\t["NPCs"] = {\n\t\t[18684] = "Bro\'Gaz the Clanless",\n\t\t[32491] = "Time-Lost Proto Drake",\n\t},\n\t["Version"] = "3.3.5.5",\n\t["NPCWorldIDs"] = {\n\t\t[18684] = 3,\n\t\t[32491] = 4,\n\t},\n}\n\n```\n\n## `SLPP.decode()` output (not what I was looking for)\n\n```lua\n\n-- This is a lua file from the game World of Warcraft: Wrath of the Lich King\n-- I need those keys sorted, because WoW/Lua keeps moving around the keys for\n-- no good damn reason >:(\n-- HOW DO YOU EXPECT ME TO TRACK MY SETTINGS IN A REPO, BLIZZARD!?\n-- jk, I know Wrath is still relatively rough around the edges.\n\n\n["_NPCScanOptionsCharacter"] = {\n\t["Achievements"] = {\n\t\t[1312] = true,\n\t\t[2257] = true\n\t},\n\t["NPCWorldIDs"] = {\n\t\t[18684] = 3,\n\t\t[32491] = 4\n\t},\n\t["NPCs"] = {\n\t\t[18684] = "Bro\'Gaz the Clanless",\n\t\t[32491] = "Time-Lost Proto Drake"\n\t},\n\t["Version"] = "3.3.5.5"\n}\n\n```\n\nNote the lack of trailing comma\'s, and _NPCScanOptionsCharacter being wrapped\nin quotes and brackets.\n\n## `big_slpp.utils.unwrap()`\'s output\n\n```lua\n\n_NPCScanOptionsCharacter = {\n\t["Achievements"] = {\n\t\t[1312] = true,\n\t\t[2257] = true,\n\t},\n\t["NPCWorldIDs"] = {\n\t\t[18684] = 3,\n\t\t[32491] = 4,\n\t},\n\t["NPCs"] = {\n\t\t[18684] = "Bro\'Gaz the Clanless",\n\t\t[32491] = "Time-Lost Proto Drake",\n\t},\n\t["Version"] = "3.3.5.5",\n}\n```\n\nPractically the same, but sorted! :D\nAlso, trailing comma\'s!\n',
    'author': 'NostraDavid',
    'author_email': '55331731+nostradavid@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NostraDavid/big-slpp',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
