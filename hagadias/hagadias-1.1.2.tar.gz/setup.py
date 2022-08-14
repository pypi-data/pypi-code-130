# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hagadias']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0',
 'anytree>=2.8.0,<3.0.0',
 'lxml>=4.9.1,<5.0.0',
 'pefile>=2022.5.30,<2023.0.0']

setup_kwargs = {
    'name': 'hagadias',
    'version': '1.1.2',
    'description': 'Extract game data from the Caves of Qud roguelike',
    'long_description': '# hagadias\n\nPython package to extract game data from the [Caves of Qud](http://www.cavesofqud.com/) roguelike.\n\nThis library forms the base for several projects:\n\n- the Caves of Qud wiki bot that builds and updates the [official Caves of Qud wiki](https://wiki.cavesofqud.com/)\n- the Discord bot that operates on the [Caves of Qud discord server](https://discordapp.com/invite/cavesofqud) (invite\n  link)\n\n## What does it do?\n\nhagadias allows a user to read game data in the raw format used by the\n[Caves of Qud](http://www.cavesofqud.com/) roguelike RPG, including the object tree, fully colored tiles, and character\ndata. It needs to be passed a path to a local installation of the game in order to do anything.\n\n## Installation\n\nhagadias requires Python 3.10.\n\nTo install the package from this GitHub repository without a package manager, run  \n`pip install git+https://github.com/trashmonks/hagadias@main#egg=hagadias`  \nIf you\'re using pipenv to manage dependencies,  \n`pipenv install -e git+https://github.com/trashmonks/hagadias.git@main#egg=hagadias`\nIf you\'re using Poetry to manage dependencies,\n`poetry add git+https://github.com/trashmonks/hagadias#main`\n\n## Tile support\n\nTile support requires the texture files from Caves of Qud to be unpacked into a "Textures" directory under the working\ndirectory of your project that is importing hagadias. You can use the\n[Brinedump](https://github.com/TrashMonks/brinedump)\ngame mod to export these textures from within the game.\n\n## Example usage\n### Startup\n```python\nimport hagadias\nfrom pprint import pprint\nGAMEPATH = \'C:\\\\Steam\\\\steamapps\\\\common\\\\Caves of Qud\'  # Windows\n# GAMEPATH = \'~/.local/share/Steam/steamapps/common/Caves of Qud\'  # Linux\n# GAMEPATH = \'~/Library/Application Support/Steam/steamapps/common/Caves of Qud\'  # macOS\nroot = hagadias.gameroot.GameRoot(GAMEPATH)\nprint(root.gamever)  # output version of the game\n```\n```\n2.0.203.56\n```\n\n### Objects (Blueprints)\n```\nqud_object_root, qindex = root.get_object_tree()\n\n# The above gives you two items:\n# - a `qud_object_root` object of type `QudObjectProps` that is the root of the CoQ object hierarchy, allowing you to traverse the entire object tree and retrieve information about the items, characters, tiles, etc.\n# - a `qindex` which is a dictionary that simply maps the Name (ingame object ID or wish ID) of each ingame object, as a string, to the Python object representing it.\n\n# Example use of qud_object_root:\n>>> qud_object_root.source\n\'<object Name="Object">\\n    <part Name="Physics" Conductivity="0" IsReal="true" Solid="false" Weight="0"></part>\\n  </object>\'\n\n# But what you really want is the qindex:\n>>> snapjaw = qindex[\'Snapjaw\']\n>>> snapjaw.desc\n\'Tussocks of fur dress skin stretched over taut muscle. Upright =pronouns.subjective= =verb:stand:afterpronoun=, but =pronouns.subjective= =verb:look:afterpronoun= ready to drop onto fours. =pronouns.Possessive= snout snarls and =pronouns.possessive= ears twitch. =pronouns.Subjective= =verb:bark:afterpronoun=, and =pronouns.possessive= hyena tribesmen answer.\'\n\n>>> snapjaw.dv\n6\n\n>>> help(snapjaw)\n# will give detailed help on all properties and methods, including a long list of properties that objects can have, like below:\n...\n\n |  butcheredinto\n |      What a corpse item can be butchered into.\n |  \n |  canbuild\n |      Whether or not the player can tinker up this item.\n |  \n |  candisassemble\n |      Whether or not the player can disassemble this item.\n |  \n |  carrybonus\n |      The carry weight bonus.\n\n# and so on.\n\n# Tile support requires you to download the modding tile toolkit, described in the section above. But with it, you can do:\n\n>>> youngivory = qindex[\'Young Ivory\']\n\n>>> youngivory.tile\n<hagadias.qudtile.QudTile object at 0x0000018F898C3BA8>\n\n>>> youngivory.tile.image\n<PIL.PngImagePlugin.PngImageFile image mode=RGBA size=16x24 at 0x18F890B3320>\n\n# for a PIL library format PNG image. There are other methods for retrieving BytesIO PNG binary data, see\n>>> help(youngivory.tile)\n# for details.\n```\n\n### Character codes\n```python\ngamecodes = root.get_character_codes()\n# A dictionary containing some helpful information used to calculate the results of character builds.\n# `gamecodes` contains the following items:\n# \'class_bonuses\': a dictionary mapping castes+callings to lists of stat bonuses\n# \'class_skills\': a dictionary mapping castes+callings to lists of skills (e.g. \'Horticulturalist\': [\'Meal Preparation\', ...]\n# \'class_tiles\': a dictionary mapping castes+callings to tuples of (tile path, detail color) for that caste/calling\'s art\nprint(hagadias.character_codes.STAT_NAMES)\nprint(gamecodes["class_bonuses"]["Horticulturist"])  # 3-point Intelligence bonus\nprint(gamecodes["class_skills"]["Horticulturist"])\nprint(gamecodes["class_tiles"]["Horticulturist"])\n```\n```\n(\'Strength\', \'Agility\', \'Toughness\', \'Intelligence\', \'Willpower\', \'Ego\')\n[0, 0, 0, 3, 0, 0]\n[\'Meal Preparation\', \'Harvestry\', \'(Axe)\', \'(Bow and Rifle)\', \'Wilderness Lore: Jungles\']\n(\'creatures/caste_1.bmp\', \'g\')\n```\n\n## Contributing\n\nSee `CONTRIBUTING.md`.\n\n## Contributors\n\nThank you to the following people who have contributed code to this project:\n\n- egocarib\n- Wreckstation\n- librarianmage\n- HeladoDeBrownie\n- elvres\n- robbyblum\n',
    'author': 'syntaxaire',
    'author_email': 'syntaxaire@gmail.com',
    'maintainer': 'syntaxaire',
    'maintainer_email': 'syntaxaire@gmail.com',
    'url': 'https://github.com/TrashMonks/hagadias',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
