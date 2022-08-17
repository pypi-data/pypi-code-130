# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fortilib', 'fortilib.mixins']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<0.24.0']

setup_kwargs = {
    'name': 'fortilib',
    'version': '0.1.1',
    'description': 'fortilib - a Python Library to interact with Fortigate Firewalls',
    'long_description': '# fortilib - a Python Library to interact with Fortigate Firewalls\n\nThis Python module contains the ability to get and configure following object on [Fortigate Firewalls](https://www.fortinet.com/products/next-generation-firewall):\n* Addresses\n* Address Groups\n* Interfaces\n* IPPools\n* Policies\n* Proxy Addresses\n* Proxy Address Groups\n* Proxy Policies\n* Routes\n* Services\n* Service Groups\n* Vips\n* Vip Groups\n\n## Installation\nPython >= 3.8 is required.\n\nDependencies:\n* [httpx](https://www.python-httpx.org/)\n\nSimply install fortilib via pip:\n```\n> pip install fortilib\n```\n\n## Quickstart\n\n```python\nimport ipaddress\n\nfrom fortilib.firewall import FortigateFirewall\nfrom fortilib.fortigateapi import FortigateFirewallApi\nfrom fortilib.address import FortigateIpMask\n\n\napi = FortigateFirewallApi(\n    "127.0.0.1", # firewall ip\n    "username",\n    "password",\n    "vdom", # use "root" if you dont have vdoms activated\n)\nfirewall = FortigateFirewall("fw01", api)\nfirewall.login()\n\n# load all objects from fortigate\nfirewall.get_all_objects()\n\n# create an firewall address\naddress = FortigateIpMask()\naddress.name = "Test Address"\naddress.subnet = ipaddress.ip_network("127.0.0.1/32")\n\n# add object to firewall\nfirewall.create_firewall_address(address)\n\n# print all addresses on firewall\nfor address in firewall.addresses:\n    print(address.name)\n```\n\n## Contributing\n\nSee [Contributing](CONTRIBUTING.md).\n\n## License\n\nGPLv3\n',
    'author': 'Daniel Zinke',
    'author_email': 'Daniel.Zinke@t-systems.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
