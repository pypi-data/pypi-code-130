# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bamboo',
 'bamboo.api',
 'bamboo.cli',
 'bamboo.request',
 'bamboo.sticky',
 'bamboo.util']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['bamboo = bamboo.cli:main']}

setup_kwargs = {
    'name': 'bamboo-core',
    'version': '0.10.5',
    'description': 'General purpose server framework in Python',
    'long_description': '# bamboo\n\n[![bamboo](https://github.com/jjj999/bamboo/blob/main/docs/res/bamboo.png?raw=true)](https://jjj999.github.io/bamboo/)\n[![PyPI version](https://badge.fury.io/py/bamboo-core.svg)](http://badge.fury.io/py/bamboo-core)\n[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.python.org/pypi/bamboo-core/)\n[![](https://img.shields.io/badge/docs-stable-blue.svg)](https://jjj999.github.io/bamboo)\n\n## Supported Interfaces\n\n- WSGI\n- ASGI v3.0 (HTTP, WebSocket and Lifespan)\n\n## Installing\n\n* Python: >= 3.7\n\n```\npython -m pip install bamboo-core\n```\n\n## [Usage](https://jjj999.github.io/bamboo/tutorials/concept/)\n\n以下は簡単な実装例です．\n\n```python\nfrom bamboo import WSGIApp, WSGIEndpoint, WSGITestExecutor\n\napp = WSGIApp()\n\n@app.route("hello")\nclass MockEndpoint(WSGIEndpoint):\n\n    def do_GET(self) -> None:\n        self.send_body(b"Hello, World!")\n\nif __name__ == "__main__":\n    WSGITestExecutor.debug(app)\n```\n\n上記スクリプトを実行後，ブラウザで http://localhost:8000/hello にアクセスするとレスポンスを確認できます．\n\n## API documentation\n\nAPI ドキュメントは[こちら](https://jjj999.github.io/bamboo/api/bamboo/pkg/)．\n\n## Examples\n\n### [upsidedown](https://github.com/jjj999/bamboo/tree/main/examples/upsidedown)\n\nリクエストされた文字列を逆順に反転させて返すアプリケーションです．\n\n### [image_traffic](https://github.com/jjj999/bamboo/tree/main/examples/image_traffic)\n\nアクセスに対して静的な画像を返すアプリケーションです．\n\n### [tweets](https://github.com/jjj999/bamboo/tree/main/examples/tweets)\n\nCLI ベースの簡易的な Twitter のような投稿アプリです．認証機能は実装されていません．\n',
    'author': 'jjj999',
    'author_email': 'jjj999to@gmail.com',
    'maintainer': 'jjj999',
    'maintainer_email': 'jjj999to@gmail.com',
    'url': 'https://jjj999.github.io/bamboo',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
