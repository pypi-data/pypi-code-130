# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['gmaps_tracker']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'geographiclib>=2.0,<3.0',
 'locationsharinglib>=4.1.8,<5.0.0']

entry_points = \
{'console_scripts': ['gmaps_tracker = gmaps_tracker.gmaps_tracker:run']}

setup_kwargs = {
    'name': 'gmaps-tracker',
    'version': '1.0.0',
    'description': 'Tool for storing shared locations',
    'long_description': '# gmaps_tracker\nLogging of locations of shared connections from Google Maps.\n\nThe project is under construction.\n\n## Prerequisits\n - Cookies for authentication. See next chapter how to get them.\n\n### How to get get cookies.txt for Google maps\nFirefox:\n - Install addon: [export-cookies-txt](https://addons.mozilla.org/en-US/firefox/addon/export-cookies-txt)\n - Log in with your user to open [google.com/maps](https://www.google.com/maps)\n - Click on addon logo / "Export cookies for google.com"\n - Save the file as cookies.txt in the root of this project\n\nChrome:\n - Extension: [get-cookiestxt](https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid) extension for Chrome\n   - Log in with your user to open [google.com/maps](https://www.google.com/maps)\n   - Click on the icon of the extension & export the cookies as file\n\n\n\n',
    'author': 'Sandor Berczi',
    'author_email': 'Berczi.Sandor@gmail.com',
    'maintainer': 'Sandor Berczi',
    'maintainer_email': 'Berczi.Sandor@gmail.com',
    'url': 'https://github.com/BercziSandor/gmaps_tracker/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
