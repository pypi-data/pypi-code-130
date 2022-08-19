# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['harmony_auth']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.79.0,<0.80.0',
 'httpx>=0.23.0,<0.24.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'redis[hiredis]>=4.3.4,<5.0.0',
 'uvicorn>=0.18.2,<0.19.0']

setup_kwargs = {
    'name': 'harmony-auth',
    'version': '0.1.5',
    'description': 'Discord OAuth2 Implicit Grant Dependency for FastAPI',
    'long_description': '# Harmony Auth\n\nDiscord OAuth2 Implicit Grant thingy for FastAPI.\n\nTokens are cached in Redis with the user\'s information & guilds (if enabled)\n\nYes. I know this is a mess. :)\n\n## Server Usage\n\n```python\nfrom harmony_auth import HarmonyAuth\nfrom fastapi import FastAPI, Depends\n\nauth = HarmonyAuth()\napp = FastAPI()\n\n\n@app.get(\'/secure\')\nasync def secure_route(user=Depends(auth)):\n    return user\n\n```\n\n## Client Usage\n1. [Request an implicit grant access token from Discord](https://discord.com/developers/docs/topics/oauth2#implicit-grant)\n2. Pass received `access_token` to any endpoint with the Harmony Auth dependency to login and access resources.\n\n```sh\ncurl -X GET --location "http://127.0.0.1:8000/secure" \\\n    -H "Accept: application/json" \\\n    -H "Authorization: Bearer {{access_token}}"\n```\n\n### Reload User Data\nIf you need to reload the user\'s data in the cache (if they joined a guild, for example), call `get_user(token, force_fetch=True)`\n\nExample:\n```python\n@app.get("/refresh")\nasync def refresh_user_data(token: str = Depends(auth.token)):\n    user = await auth.get_user(token, force_fetch=True)\n    ...\n```\nThis will update the cache and return the user.\n\n### Log Out / Revoke token\nUse `revoke_token(token)` to remove user data from the cache. This removes all the cached user information.\n\nIf you specify a `client_id` and `client_secret`, _Harmony Auth_ will request that Discord revokes the token.\n\n### Q: How do I log in?\nA: You don\'t need to log in. Just provide a valid access token.\n\n## Rate limit protections\nI personally don\'t want to handle this, so I am using [twilight-http-proxy](https://github.com/twilight-rs/http-proxy).\n\nTODO: Create fork to add OAuth2 routes to twilight http proxy.\n',
    'author': 'William Hatcher',
    'author_email': 'william@hatcher.work',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/williamhatcher/harmonyAuth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
