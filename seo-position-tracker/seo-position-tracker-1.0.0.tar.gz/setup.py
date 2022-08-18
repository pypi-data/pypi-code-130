# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['seo_position_tracker']

package_data = \
{'': ['*']}

install_requires = \
['google-search-results>=2.4.1,<3.0.0', 'pandas>=1.4.3,<2.0.0']

setup_kwargs = {
    'name': 'seo-position-tracker',
    'version': '1.0.0',
    'description': 'A simple Python package for SEO position tracking from Google and other search engines.',
    'long_description': '<h1 align="center">SEO Position Tracker 📡</h1>\n\n<p align="center">A simple Python tool for SEO position tracking from Google and other search engines.</p>\n\n<div align="center">\n\n  <a href="https://pepy.tech/project/seo-position-tracker">![Downloads](https://static.pepy.tech/personalized-badge/seo-position-tracker?period=month&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads)</a>\n  <a href="">![licence](https://img.shields.io/github/license/dimitryzub/seo-position-tracker?color=blue)</a>\n\n</div>\n\n\n## 🔎 Current search engines support\n\n- Google Search - looks for first 100 organic results.\n- [See what\'s coming next](https://github.com/dimitryzub/seo-position-tracker/projects).\n\n\n## ⚙️Installation\n\n```bash\n$ pip install seo-position-tracker\n```\n\n```bash\n$ git clone https://github.com/dimitryzub/seo-position-tracking.git\n```\n\n\n## 🤹\u200d♂️Usage\n\n#### Available CLI arugments:\n\n```bash\n$ python seo_position_tracker.py -h \n```\n\n```lang-none\nSerpApi SEO position tracker.\n\noptional arguments:\n  -h, --help         show this help message and exit\n  --api-key API_KEY  your SerpApi API key. For more: https://serpapi.com/manage-api-key\n  -se SE             search engine. Currently only one can be passed. Default: Google\n  -po                returns website position only.\n  -q Q               search query. Default: "Coffee"\n  -tk TK             target keyword to track. Default: "coffee". Currently only one can be passed.\n  -tw TW             target website to track. Default: "starbucks.com". Currently only one can be passed.\n  -l L               language of the search. Default: "en" - English. For more: https://serpapi.com/google-languages\n  -c C               country of the search. Default: "us" - United States. For more: https://serpapi.com/google-countries\n  -loc LOC           location of the search. Default: "United States". For more: https://serpapi.com/locations-api\n  --to-csv           saves results in the current directory to csv.\n  --to-json          saves results in the current directory to json.\n```\n\n#### Example:\n\n```bash\n$ python seo_position_tracker.py --api-key=<your_serpapi_api_key> \\\n> -q="minecraft buy" \\\n> -tk minecraft \\\n> -tw minecraft.net \\\n> -l en -c us\n```\n\n```json\n[\n  {\n    "position": 1,\n    "country_of_the_search": "us",\n    "title": "Get Minecraft: Gaming Platform Features",\n    "link": "https://www.minecraft.net/en-us/get-minecraft"\n  },\n  {\n    "position": 5,\n    "country_of_the_search": "us",\n    "title": "I Want to Buy Minecraft on a Non-Windows Device",\n    "link": "https://help.minecraft.net/hc/en-us/articles/6661712171405-I-Want-to-Buy-Minecraft-on-a-Non-Windows-Device"\n  }\n]\n```\n\n\n\n#### Get position only\n\n```bash\n$ python seo_position_tracker.py --api-key=<your_serpapi_api_key> \\\n> -q="minecraft buy" \\\n> -tk minecraft \\\n> -tw  minecraft.net \\\n> -l en -c us \\\n> -po\n```\n\n```lang-none\n[1]\n# or \n[1, 5, ...]\n```\n\n## 💡Issues or suggestions\n\nVisit [issues](https://github.com/dimitryzub/seo-position-tracking/issues) page.\n\n## 📜 Licence\n\nSEO Position Tracker is released under the [BSD-3-Clause Licence](https://github.com/dimitryzub/seo-position-tracker/blob/407a561b23e0905d88e4d9dd22390330e96889e1/LICENSE).\n\n',
    'author': 'Dimitry Zub',
    'author_email': 'dimitryzub@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dimitryzub/seo-position-tracker',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
