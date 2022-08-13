# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nautobot_ssot_vsphere',
 'nautobot_ssot_vsphere.diffsync',
 'nautobot_ssot_vsphere.diffsync.adapters',
 'nautobot_ssot_vsphere.diffsync.adapters.shared',
 'nautobot_ssot_vsphere.management',
 'nautobot_ssot_vsphere.management.commands',
 'nautobot_ssot_vsphere.tests',
 'nautobot_ssot_vsphere.tests.fixtures',
 'nautobot_ssot_vsphere.utilities']

package_data = \
{'': ['*'], 'nautobot_ssot_vsphere': ['static/nautobot_ssot_vsphere/*']}

install_requires = \
['diffsync>=1.4.3,<2.0.0',
 'nautobot-ssot>=1.1.0,<2.0.0',
 'netutils>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'nautobot-ssot-vsphere',
    'version': '0.1.3',
    'description': 'Nautobot SSoT vSphere',
    'long_description': '# Nautobot SSoT vSphere\n\nA plugin for [Nautobot](https://github.com/nautobot/nautobot) that leverages the SSoT plugin to create Virtual Machines, VMInterfaces, IPAddresses, Clusters, and Cluster Groups from VMWare vSphere.\n\n![JobOverview](docs/images/job_overview.png) ![VirtualMachines](docs/images/virtualmachines.png)\n\n## The future of Virtual Machine In Nautobot\n\nThere is discussion in place to that will bring big changes to VirtualMachine and VMInterface targeted for release 2.0. See the [issue](https://github.com/nautobot/nautobot/issues/1178)\n\nWhen that time comes, this application will need to be updated to handle the new core model structure\n\n## Installation\n\nThe plugin is available as a Python package in pypi and can be installed with pip\n\n```shell\npip install nautobot-ssot-vsphere\n```\n\n> The plugin is compatible with Nautobot 1.2.0 and higher\n\nTo ensure Nautobot SSoT vSphere is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the Nautobot root directory (alongside `requirements.txt`) and list the `nautobot-ssot-vsphere` package:\n\n```no-highlight\n# echo nautobot-ssot-vsphere >> local_requirements.txt\n```\n\nOnce installed, the plugin needs to be enabled in your `nautobot_config.py`\n\n```python\n# In your nautobot_config.py\nPLUGINS = ["nautobot_ssot_vsphere"]\n\nPLUGINS_CONFIG = {\n    "nautobot_ssot_vsphere": {\n        "VSPHERE_URI": os.getenv("VSPHERE_URI"),\n        "VSPHERE_USERNAME": os.getenv("VSPHERE_USERNAME"),\n        "VSPHERE_PASSWORD": os.getenv("VSPHERE_PASSWORD"),\n        "VSPHERE_VERIFY_SSL": is_truthy(os.getenv("VSPHERE_VERIFY_SSL", False)),\n    },\n}\n```\n\nThe plugin behavior can be controlled with additional configuration settings\n\n```bash\n- `VSPHERE_TYPE` Defaults to `VMWare vSphere`\n- `ENFORCE_CLUSTER_GROUP_TOP_LEVEL` Defaults to True\n- `VSPHERE_VM_STATUS_MAP` Defaults to {"POWERED_OFF": "Offline", "POWERED_ON": "Active"}\n- `VSPHERE_IP_STATUS_MAP` Defaults to {"PREFERRED": "Active", "UNKNOWN": "Reserved"}\n- `VSPHERE_VM_INTERFACE_MAP` Defaults to {"NOT_CONNECTED": False, "CONNECTED": True}\n- `PRIMARY_IP_SORT_BY` Defaults to "Lowest"\n- `DEFAULT_USE_CLUSTERS` Defaults to `True`\n- `DEFAULT_CLUSTER_NAME` Defaults to "vSphere Default Cluster"\n- `DEFAULT_IGNORE_LINK_LOCAL` Defaults to `True`\n```\n\nTo get a detailed description on each configuration setting, head over to the [Overview](https://h4ndzdatm0ld.github.io/nautobot-ssot-vsphere/overview.html) documentation.\n',
    'author': 'h4ndzdatm0ld',
    'author_email': 'hugotinoco@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/h4ndzdatm0ld/nautobot-ssot-vsphere',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
