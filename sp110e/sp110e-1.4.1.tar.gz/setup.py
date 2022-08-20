# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sp110e']

package_data = \
{'': ['*']}

install_requires = \
['bleak==0.15.1', 'syncer==1.3.0']

setup_kwargs = {
    'name': 'sp110e',
    'version': '1.4.1',
    'description': 'Control SP110E BLE RGB LED device from computer',
    'long_description': "# SP110E Python Library\n\nControl SP110E BLE RGB LED device from computer\n\n## Install\n\n```bash\npip install sp110e\n```\n\n## Tools\n\n- Controller: High-level SP110E asynchronous controller. Use it only in asynchronous environment (with `asyncio`)\n- ControllerSync: Synchronous adapter for high-level SP110E asynchronous controller. Handy tool to use from Python shell or synchronous (normal) environment\n- Driver: Low-level SP110E asynchronous BLE driver based on bleak library. Use it only if you know why\n\n## Documentation\n\n[Full API Reference](./docs)\n\n## Examples\n\nQuick start:\n\n```python\nfrom sp110e.controller_sync import ControllerSync\n\ndevice = ControllerSync('AF:00:10:01:C8:AF')\ndevice.switch_on()\ndevice.set_color([255, 0, 0])\ndevice.set_brightness(255)\n```\n\n[More examples](examples)\n\n## Development\n\n### Create new release\n\nPush changes to 'main' branch following [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).\n\n### Update documentation\n\n`docs` folder is being updated automatically by GitHub Actions when source files are changed.\n\n## Integrations\n\n- [SP110E Home Assistant Integration](https://github.com/roslovets/SP110E-HASS)\n\n## Useful links\n\n- [SP110E API Reference](https://gist.github.com/mbullington/37957501a07ad065b67d4e8d39bfe012)\n- [Vox](https://github.com/nguyenthuongvo/Vox)\n- [bleak library](https://github.com/hbldh/bleak)\n- [Reverse engineering simple BLE](http://nilhcem.com/iot/reverse-engineering-simple-bluetooth-devices)\n",
    'author': 'Pavel Roslovets',
    'author_email': 'p.v.roslovets@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/roslovets/SP110E',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
