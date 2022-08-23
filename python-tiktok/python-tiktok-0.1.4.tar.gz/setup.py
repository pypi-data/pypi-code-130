# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytiktok', 'pytiktok.models']

package_data = \
{'': ['*']}

install_requires = \
['dataclasses-json>=0.5.7,<0.6.0', 'requests>=2.24,<3.0']

setup_kwargs = {
    'name': 'python-tiktok',
    'version': '0.1.4',
    'description': 'A simple Python wrapper for Tiktok API. ✨ 🍰 ✨',
    'long_description': 'python-tiktok\n\nA simple Python wrapper around for Tiktok API :sparkles: :cake: :sparkles:.\n\n.. image:: https://img.shields.io/badge/TikTok-%23000000.svg?style=for-the-badge&logo=TikTok&logoColor=white\n   :target: https://developers.tiktok.com/\n   :alt: tiktok\n\n.. image:: https://img.shields.io/pypi/v/python-tiktok.svg\n    :target: https://pypi.org/project/python-tiktok/\n    :alt: PyPI\n\n============\nIntroduction\n============\n\nThis library provides a service to easily use TikTok official apis.\n\nFor now, include follows apis:\n\n- `TikTok for developers <https://developers.tiktok.com/>`_\n- `TikTok for Business Account <https://ads.tiktok.com/marketing_api/docs?id=1732701966223426>`_\n\n==========\nInstalling\n==========\n\nYou can install this library easily by `pypi`:\n\n.. code-block:: shell\n\n    $ pip install python-tiktok\n\nMore installing detail see `Installation docs <https://sns-sdks.lkhardy.cn/python-tiktok/installation/>`_\n\n=====\nUsing\n=====\n\nYou can see more usage detail at `usage docs <https://sns-sdks.lkhardy.cn/python-tiktok/usage/preparation/>`_\n\n----------------\nBusiness Account\n----------------\n\n.. tip::\n\n    API for Business Version ``1.3`` is now live! visit `here <https://ads.tiktok.com/marketing_api/docs?id=1740579480076290>`_ for more details.\n\n    Now this library set default version to ``v1.3``.\n\n    And ``v1.2`` will be deprecated on August 15, 2023.\n\nIf you have account access token, you can initialize api instance by it.\n\n.. code-block:: python\n\n    >>> from pytiktok import BusinessAccountApi\n    >>> business_api = BusinessAccountApi(access_token="Your Access Token")\n\nOr you can let account to give permission by `OAuth flow`. See `business authorization docs <https://sns-sdks.lkhardy.cn/python-tiktok/authorization/business-authorization/>`_\n\nNow you can get account\'s data.\n\nGet account profile:\n\n.. code-block:: python\n\n    >>> business_api.get_account_data(business_id="Business ID", return_json=True)\n    >>> # {\'code\':0,\'message\':\'OK\',\'request_id\':\'2022070106561301000400402500400500600301500A52386\',\'data\':{\'display_name\':\'kiki\',\'profile_image\':\'https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/accb4aeac4ec812e2bdc45ce1da1ed39~c5_168x168.jpeg?x-expires=1656828000&x-signature=MmXPWeImP%2BRGBwAOqN3wjPpDiZE%3D\'}}\n\nIf you set function parameter `return_json` to `True`, will return the json dict data. Otherwise will return a `dataclass` object representing the response.\n\nGet account videos:\n\n.. code-block:: python\n\n    >>> business_api.get_account_videos(business_id="Business ID", return_json=True)\n    >>> # {\'code\':0,\'message\':\'OK\',\'request_id\':\'20220701071724010004003007735002053068B3FD9\',\'data\':{\'videos\':[{\'item_id\':\'7108684822863760646\'},{\'item_id\':\'7109064881462152453\'}],\'has_more\':False,\'cursor\':0}}\n\n-------\nKit Api\n-------\n\nIf you have user access token, you can initialize api instance by it.\n\n.. code-block:: python\n\n    >>> from pytiktok import KitApi\n    >>> kit_api = KitApi(access_token="Your Access Token")\n\nOr you can let user to give permission by `OAuth flow`. See `kit authorization docs <https://sns-sdks.lkhardy.cn/python-tiktok/authorization/kit-authorization/>`_\n\nNow you can get account\'s data.\n\nGet user info:\n\n.. code-block:: python\n\n    >>> kit_api.get_user_info(open_id="User Openid", return_json=True)\n    >>> # {\'data\':{\'user\':{\'open_id\':\'open_id\',\'union_id\':\'union_id\',\'avatar_url\':\'https://p16-sign-sg.tiktokcdn.com/tiktok-obj/7046311066329939970~c5_168x168.jpeg?x-expires=1656907200&x-signature=w4%2FugSm2IOdma6p0D9V%2FZneIlPU%3D\',\'display_name\':\'ki\'}},\'error\':{\'code\':0,\'message\':\'\'}}\n\nGet user videos:\n\n.. code-block:: python\n\n    >>> kit_api.get_user_videos(open_id="_000Hqnyyz5UYe39YWBZwFnaQGfyaoh3s4IY", return_json=True)\n    >>> # {\'data\':{\'videos\':[{\'create_time\':1654670085,\'share_url\':\'https://www.tiktok.com/@klein_kunkun/video/7106753891953347842?utm_campaign=tt4d_open_api&utm_source=aw46lwwtsqjeapig\',\'duration\':5,\'id\':\'7106753891953347842\'},{\'create_time\':1654658105,\'share_url\':\'https://www.tiktok.com/@klein_kunkun/video/7106702437926407426?utm_campaign=tt4d_open_api&utm_source=aw46lwwtsqjeapig\',\'duration\':6,\'id\':\'7106702437926407426\'}],\'cursor\':1654658105000,\'has_more\':False},\'error\':{\'code\':0,\'message\':\'\'}}\n',
    'author': 'ikaroskun',
    'author_email': 'merle.liukun@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sns-sdks/python-tiktok',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
