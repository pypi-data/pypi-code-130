# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['saleor_flat_tax_plugin']

package_data = \
{'': ['*']}

entry_points = \
{'saleor.plugins': ['saleor_flat_tax_plugin = '
                    'saleor_flat_tax_plugin.plugin:FlatTaxPlugin']}

setup_kwargs = {
    'name': 'saleor-flat-tax-plugin',
    'version': '0.5.1',
    'description': 'Saleor Flat Tax Plugin',
    'long_description': "# Saleor Flat Tax Plugin\n\n`saleor-flat-tax-plugin` is a small plugin to enable flat taxes in Saleor.\n\nIt's based out of Saleor's\n[VatlayerPlugin](https://github.com/saleor/saleor/blob/main/saleor/plugins/vatlayer/plugin.py#L49). Using the same\ncalculations but modified to use the taxes configured through the plugin and not take Country into consideration.\n\n_Disclaimer_: This project is not connected/endorsed by saleor's community\n\n## Installation ##\n\nUsing pip:\n\n```bash\npip install saleor-flat-tax-plugin\n```\n\nOnce installed Saleor will automatically detect the plugin, and you'll be able to see it in Saleor's dashboard",
    'author': 'Carlos Ramírez',
    'author_email': 'carlosarg54@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/carlosa54/saleor-flat-tax-plugin',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
