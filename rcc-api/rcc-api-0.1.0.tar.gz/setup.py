# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['RCC', 'RCC.api', 'RCC.types']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'pydantic>=1.9.2,<2.0.0']

setup_kwargs = {
    'name': 'rcc-api',
    'version': '0.1.0',
    'description': 'Обертка для работа с апи RCC',
    'long_description': '# RustCheatCheck API\nУдобная обертка для взаимодействия с апи [RCC](https://rustcheatcheck.ru/). \n# Как начать?\n\n## Установка \n```\npip install rcc-api\n```\n## Взаимодействие\n```python\nimport asyncio\nimport RCC\n\n\nasync def main():\n    api = RCC.API("TOKEN/KEY")\n\n    # Здесь показаны не все методы, более подробнее информация\n    # Находится здесь https://rustcheatcheck.ru/panel/getapi\n    # Некоторые поля/методы названы более правильно(по моему мнению)\n    # Ваш редактор в любом случае вам подскажет\n\n    # Получение информация об аккаутне\n    player = await api.get_info(76561198021247080)\n    print(player.steamid)  # 76561198021247080\n    print(player.rcc_checks)  # 7\n    checks = player.checks\n    print(checks[1].time)  # 2019-01-08 16:53:13+00:00\n    print(checks[1].server_name)  # MagicRust\n    bans = player.bans\n    print(bans[0].reason)  # мамкин_крашер\n    print(bans[0].active)  # False\n    print(bans[0].ban_date)  # 2019-06-11 12:01:07+00:00ет\n\n    # Выдача доступа к чекеру\n    response = await api.start_check(76561198021247080,  moder_steamid=76561198021247080)\n    print(response.status)  # success\n    print(response.error)  # None\n\n    # Выдача бана\n    response = await api.ban_player(76561198021247080, "macros")\n    print(response.status)  # success\n    print(response.error)  # None\n\n    # Снятие бана\n    response = await api.unban_player(76561198021247080)\n    print(response.status)  # success\n    print(response.error)  # None\n\n    # Работа с ошибками\n    try:\n        player = await api.get_info(62485679287628672076)\n    except RCC.exceptions.RCCErrors as e:\n        print(e)\n\n\nasyncio.run(main())\n\n```\n',
    'author': 'MaHryCT3',
    'author_email': 'mahryct123@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MaHryCT3/RCC_api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
