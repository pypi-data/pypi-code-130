# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chipscopy',
 'chipscopy._cli',
 'chipscopy.api',
 'chipscopy.api._detail',
 'chipscopy.api.ddr',
 'chipscopy.api.device',
 'chipscopy.api.hbm',
 'chipscopy.api.ibert',
 'chipscopy.api.ibert.eye_scan',
 'chipscopy.api.ibert.link',
 'chipscopy.api.ibert.yk_scan',
 'chipscopy.api.ila',
 'chipscopy.api.noc',
 'chipscopy.api.noc.graphing',
 'chipscopy.client',
 'chipscopy.client.node',
 'chipscopy.client.util',
 'chipscopy.dm',
 'chipscopy.dm.harden',
 'chipscopy.dm.harden.noc_perfmon',
 'chipscopy.examples.ddr',
 'chipscopy.examples.ibert.versal_gty',
 'chipscopy.examples.ila_and_vio',
 'chipscopy.examples.jtag',
 'chipscopy.examples.memory',
 'chipscopy.examples.noc_perfmon',
 'chipscopy.examples.program',
 'chipscopy.examples.sysmon',
 'chipscopy.proxies',
 'chipscopy.shared',
 'chipscopy.tcf',
 'chipscopy.tcf.channel',
 'chipscopy.tcf.services',
 'chipscopy.tcf.services.local',
 'chipscopy.tcf.services.remote',
 'chipscopy.tcf.tests',
 'chipscopy.tcf.util',
 'chipscopy.utils',
 'chipscopy.utils.logger',
 'chipscopy.utils.noc_utils',
 'chipscopy.xvc']

package_data = \
{'': ['*'],
 'chipscopy': ['examples/designs/vck190/production/chipscopy_ced/*',
               'examples/designs/vmk180/production/chipscopy_ced/*',
               'examples/img/*'],
 'chipscopy.examples.ila_and_vio': ['img/*']}

install_requires = \
['Click>7,<9',
 'importlib_metadata>=4.4,<5.0',
 'loguru>=0.5.0,<0.6.0',
 'more-itertools>=8.2.0,<9.0.0',
 'rich>=9.12.4,<10.0.0',
 'typing_extensions>=3.7.4,<4.0.0']

extras_require = \
{'core-addons': ['kaleido>=0.0.2,<0.0.3',
                 'plotly>=4.9.0,<5.0.0',
                 'pandas>=1.2.3,<2.0.0',
                 'matplotlib>=3.4.0,<4.0.0',
                 'PyQt5>=5.15.4,<6.0.0'],
 'jupyter': ['notebook>=6.0.3,<7.0.0', 'ipywidgets>=7.5.1,<8.0.0']}

entry_points = \
{'console_scripts': ['chipscopy-get-examples = '
                     'chipscopy._cli.example_delivery:main',
                     'csutil = chipscopy._cli._chipscopy:main']}

setup_kwargs = {
    'name': 'chipscopy',
    'version': '2022.1.1660671586',
    'description': 'Open-source project from Xilinx® that enables high-level control of Versal debug IP running in hardware',
    'long_description': '# 🐍 ChipScoPy README\n\n[![](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n![](https://raw.githubusercontent.com/Xilinx/chipscopy/master/docs/images/chipscopy_logo_head_right_transparent_background.png)\n\nChipScoPy is an open-source project from Xilinx® that enables high-level control of Versal debug IP running in hardware.\nUsing a simple Python API, developers can control and communicate with ChipScope® debug IP such as the Integrated Logic\nAnalyzer (ILA), Virtual IO (VIO), device memory access, and more.\n\n-------------------------------------------------------------------------------\n\n![](https://raw.githubusercontent.com/Xilinx/chipscopy/master/docs/images/chipscopy_overview.png)\n\n-------------------------------------------------------------------------------\n\n[ChipScoPy Overview](https://xilinx.github.io/chipscopy/2022.1/overview.html)\n\n-------------------------------------------------------------------------------\n\n[System Requirements](https://xilinx.github.io/chipscopy/2022.1/system_requirements.html)\n\n-------------------------------------------------------------------------------\n\n[ChipScoPy Installation](https://xilinx.github.io/chipscopy/2022.1/chipscopy_installation.html)\n\n-------------------------------------------------------------------------------\n\n[ChipScoPy Examples](https://github.com/Xilinx/chipscopy/tree/master/chipscopy/examples)\n\n-------------------------------------------------------------------------------\n\n[API Documentation](https://xilinx.github.io/chipscopy/)\n\n-------------------------------------------------------------------------------\n',
    'author': 'Xilinx ChipScope Team',
    'author_email': None,
    'maintainer': 'Xilinx ChipScope Team',
    'maintainer_email': None,
    'url': 'https://github.com/Xilinx/chipscopy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
