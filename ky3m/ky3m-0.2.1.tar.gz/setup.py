# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ky3m', 'ky3m.common', 'ky3m.services']

package_data = \
{'': ['*']}

install_requires = \
['toml>=0.10,<0.11']

setup_kwargs = {
    'name': 'ky3m',
    'version': '0.2.1',
    'description': 'Minecraft Mod Manager by Leon "Procybit" Shepelev',
    'long_description': '[](https://github.com/Procybit/Ky3M)\n\n[![GitHub Repo stars](https://img.shields.io/github/stars/Procybit/Ky3M?style=social)](https://github.com/Procybit/Ky3M)\n\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/ky3m?style=for-the-badge)](https://pypi.org/project/ky3m/)\n\n[![GitHub](https://img.shields.io/github/license/Procybit/Ky3M?style=for-the-badge)](https://github.com/Procybit/Ky3M/blob/master/LICENSE)\n\n[![GitHub contributors](https://img.shields.io/github/contributors/Procybit/Ky3M?style=for-the-badge)](https://github.com/Procybit/Ky3M/blob/master/CONTRIBUTORS.md) [![GitHub commit activity](https://img.shields.io/github/commit-activity/w/Procybit/Ky3M?style=for-the-badge)](https://github.com/Procybit/Ky3M/commits/) [![GitHub issues](https://img.shields.io/github/issues-raw/Procybit/Ky3M?style=for-the-badge)](https://github.com/Procybit/Ky3M/issues)\n\n# Ky3M\n\nMinecraft Mod Manager by Leon "Procybit" Shepelev\n\n## Installing\n\nVia pip:\n\n```\npip install ky3m\n```\n\nYou can also update to the latest version:\n\n```\npip install ky3m --upgrade\n```\n\n**Make sure you have Python 3.10 or above installed!**\n\n## Program launch\n\nVia terminal:\n\n```\npython -m ky3m\n```\n\n## Using the CLI\n\nIf the program is run correctly, this should be in the terminal:\n```\nKy3M :>\n```\nAt the moment, the only thing that can be entered into the CLI is methods.\n\nMethods are simple commands that work directly with Ky3M internals.\n\nThe name of the method is written in CAPITAL LETTERS, the specification fields of the method are written with spaces:\n\n```\nKy3M :> METHOD Field_1 Field_2 ANoTheR--fiEld00;[-+^ 4thFIELD\nSomething happened...\n```\n\nIf the method name starts with the "adv" prefix, then the associated log will be displayed:\n\n```\nKy3M :> advMETHOD Field_1 Field_2 ANoTheR--fiEld00;[-+^ 4thFIELD\nSomething happened...\n\nLog intercepted!\n[ky3m.methods] METHOD started!\n[ky3m.something] Something happened! (something: True)\n[ky3m.methods] METHOD ended!\n```\n\n## Methods\n\n### INSPECT\n\nOutputs all .jar files names from Minecraft mods folder.\n\nASSIGNS A UNIQUE ID TO EACH NEWLY OUTPUT FILE.\n\n### PEER `id`\n\nOutputs information about certain .jar file in Minecraft mods folder.\n\nUses `id`  assigned by *INSPECT*.\n\n### EXPEL `id`\n\nPermanently deletes certain .jar file from Minecraft mods folder.\n\nUses `id` assigned by *INSPECT*.\n\n### ADOPT `saved_id`\n\nCopies certain .jar file from Minecraft mods folder to local library.\n\nUses `saved_id` assigned by *INSPECT*.\n\nCAN INTERRUPT CLI AND REQUEST NAME OF SAVED FILE IF NEEDED.\n\nDOESN\'T DELETE CERTAIN FILE.\n\nASSIGNS A UNIQUE SAVED ID TO EACH SAVED FILE.\n\n### ADOPTS\n\nOutputs all saved .jar files names from local library.\n\n### RELEASE `saved_id`\n\nCopies certain .jar file from local library to Minecraft mods folder.\n\nUses `saved_id` assigned by *ADOPT*.\n\n### PUNISH `saved_id`\n\nPermanently deletes certain .jar file from local library.\n\nUses `saved_id` assigned by *ADOPT*.\n\n### BUNDLE `name` | `bundle_id`\n\n*Note that | separates an alternates.*\n\nIf `name` not found, creates new bundle (Ky3M modpack) and outputs created bundle\'s ID.\n\nUses `name` that is any string.\n\nASSIGNS A UNIQUE ID TO EACH CREATED BUNDLE.\n\n**ALTERNATE**\n\nIf found bundle with specified `bundle_id`, outputs the bundle info.\n\nUses `bundle_id` that is valid UUID (in any form).\n\n### BUNDLES\n\nOutputs all created bundles\' IDs and names.\n\n### BURST `bundle_id`\n\nPermanently deletes certain bundle.\n\nUses `bundle_id` assigned by *BUNDLE*.\n\n### BIND `bundle_id` `saved_id`\n\nBinds certain .jar to a certain bundle.\n\nUses `bundle_id` assigned by *BUNDLE*.\n\nUses `saved_id` assigned by *ADOPT*.\n\nASSIGNS A BIND ID (BUNDLE LOCAL) BASED ON SAVED ID.\n\n### DETACH `bundle_id` `bind_id`\n\nDetached certain .jar from a certain bundle.\n\nUses `bundle_id` assigned by *BUNDLE*.\n\nUses `bind_id` assigned by *BIND*.\n\n### APPLY `bundle_id`\n\nReleases all binded to certain bundle .jar files (see *RELEASE*).\n\nUses `bundle_id` assigned by *BUNDLE*.\n\nDOESN\'T DELETE ANY FILES.\n\n## License\nThis project follows MIT license (see [LICENSE](LICENSE)).\n',
    'author': 'Leon "Procybit" Shepelev',
    'author_email': 'kyleusnaff@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Procybit/Ky3M',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
