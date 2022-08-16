# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['faker_stalker_names',
 'faker_stalker_names.en_US',
 'faker_stalker_names.fr_FR',
 'faker_stalker_names.ru_RU',
 'faker_stalker_names.uk_UA']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'faker-stalker-names',
    'version': '0.1.2',
    'description': 'Faker provider with stalker names.',
    'long_description': '# Description\n_Faker-stalker-names_ is a provider for the [Faker](https://github.com/joke2k/faker) Python package. \n\nGenerate stalker names for your tests and other tasks. Don\'t forget your friends)\n\n# Localization\nThe following localizations are present: `ru_RU`, `en_US`, `uk_UA`, `fr_FR`.\n\n# Installation\nFrom PyPi:\n\n`pip3 install faker-stalker-names`\n\n# Usage\nJust add the `Provider` to your `Faker` instance:\n\n```\nfrom faker import Faker\nfrom faker_stalker_names.en_US import Provider as StalkerNamesProvider\n\nfake = Faker()\nfake.add_provider(StalkerNamesProvider)\n```\nOr pass it to the constructor:\n```\nfrom faker import Faker\n\nfake = Faker(includes=["faker_stalker_names"], locale="ru_RU")\n```\nNow you can start to generate data:\n```\nfake.stalker_name()\n# Яшка Нытик\n\nfake.stalker_first_name()\n# Саня\n\nfake.stalker_last_name()\n# Резкий\n```\n\nYou can specify the desired type of name (`stalker` or `bandit` are available). \nBy default, the first and last names are randomly selected.\n```\nfake.stalker_name(name_type="stalker")\n# Slava Smartass\n\nfake.stalker_first_name(name_type="bandit")\n# Vasyan\n```\n\nIn addition, a way to replace the standard `name` method at your own risk:\n```\nStalkerNamesProvider.name = StalkerNamesProvider.stalker_name\nfake = Faker()\nfake.add_provider(StalkerNamesProvider)\nfake.name()\n# Shurik Professor\n```\n',
    'author': 'Grigory Bukovsky',
    'author_email': 'booqoffsky@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/booqoffsky/faker-stalker-names',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
