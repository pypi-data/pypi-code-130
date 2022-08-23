# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['moka_python_sdk',
 'moka_python_sdk.models',
 'moka_python_sdk.models.library',
 'moka_python_sdk.models.library.entity',
 'moka_python_sdk.models.merchant',
 'moka_python_sdk.models.merchant.entity',
 'moka_python_sdk.models.oauth',
 'moka_python_sdk.models.oauth.entity',
 'moka_python_sdk.models.oauth.subscription',
 'moka_python_sdk.models.oauth.subscription.entity',
 'moka_python_sdk.models.report',
 'moka_python_sdk.models.report.entity',
 'moka_python_sdk.models.transaction',
 'moka_python_sdk.models.transaction.bill',
 'moka_python_sdk.models.transaction.bill.entity',
 'moka_python_sdk.models.transaction.entity',
 'moka_python_sdk.models.transaction.invoice',
 'moka_python_sdk.models.transaction.invoice.entity',
 'moka_python_sdk.models.transaction.order',
 'moka_python_sdk.models.transaction.order.entity',
 'moka_python_sdk.network']

package_data = \
{'': ['*']}

install_requires = \
['dacite>=1.6.0,<2.0.0', 'pyhumps>=3.7.2,<4.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'moka-python-sdk',
    'version': '0.1.1',
    'description': 'Python SDK for MOKA API',
    'long_description': '# Moka Python Library\n\nThis library is the abstraction of Moka API for access from applications written with Python.\n\n## Table of Contents\n\n- [API Documentation](#api-documentation)\n- [Requirements](#requirements)\n- [Installation](#installation)\n- [Usage](#usage)\n  - [API Key](#api-key)\n  - [Merchant](#Merchant)\n  - [Transaction](#Transaction)\n   - [Get latest transaction](#get-latest-transaction)\n   - [Get all open bills](#get-all-open-bills)\n  - [Report](#report)\n   - [Category Sales](#category-sales)\n   - [Modifier Sales](#modifier-sales)\n   - [Discount Sales](#discount-sales)\n   - [Tax Sales](#tax-sales)\n\n\n## API Documentation\nPlease check [Moka API Reference](https://api.mokapos.com/docs).\n\n## Requirements\n\nPython 3.7 or later\n\n## Installation\n\nTo use the package, run ```pip install moka-python-sdk```\n\n## Usage\n\n### API Key\n\n```python\nfrom moka_python_sdk.moka import Moka\n\nAPI_KEY = "test_f7f7955d44cd10dd2bbbdc4381eb8d4c"\nSECRET_KEY = "d269d087-25a6-49fa-b17c-22cd1b23c515"\nx = Moka(api_key=API_KEY, secret_key=SECRET_KEY, production=False)\n\n# Then access each class from x attribute\nmerchant = x.Merchant\n```\n\n\n### Merchant\nGet information about merchant\n\n#### Show Business Info\n\n```python\nmerchant = x.Merchant\nmerchant.show_business_info()\n```\n\nUsage example:\n\n```python\nAPI_KEY = "test_f7f7955d44cd10dd2bbbdc4381eb8d4c"\nSECRET_KEY = "d269d087-25a6-49fa-b17c-22cd1b23c515"\nx = Moka(api_key=API_KEY, secret_key=SECRET_KEY, production=False)\n\nmerchant = x.Merchant\n\nprint("Business Info:")\nprint(merchant.show_business_info())\n\nprint("Customer List:")\nprint(merchant.get_list_customer(\n    business_id=1,\n    mobile_device=1,\n    page=1,\n    per_page=10,\n    include_deleted=True,\n    include_loyalty=True,\n))\n\nprint("Business Checkout Setting:")\nprint(merchant.get_business_checkout_setting(\n    business_id=1,\n))\n\nprint("List Outlets:")\nprint(merchant.get_list_outlets(\n    business_id=1,\n))\n``` \n\nReference: https://api.mokapos.com/docs#tag/Business\n\n\n### Transaction\n#### Get latest transaction\n```python\ntransaction = x.Transaction\n\nprint("Show Latest Transaction:")\nprint(transaction.show_latest(\n    outlet_id=1,\n    per_page=10,\n    include_promo=True\n))\n```\nReference: https://api.mokapos.com/docs#operation/showLatestTransactionsV3\n\n#### Get all open bills\n```python\ntransaction = x.Transaction\n\nprint("Get All Open Bill: ")\nprint(transaction.bill.get(\n    outlet_id=1,\n    page=1,\n    per_page=10,\n    dine_in_only=True,\n    deep=True\n))\n```\nReference: https://api.mokapos.com/docs#operation/listBillsV1\n### Report\n#### Category Sales\n```python\nreport = x.Report\nreport.show_category_sales(\n    outlet_id=1,\n    per_page=10,\n)\n```\nReference: https://api.mokapos.com/docs#operation/showCategorySalesV2\n\n#### Modifier Sales\n```python\nreport = x.Report\nreport.show_modifier_sales(\n    outlet_id=1,\n    per_page=10,\n)\n```\nReference: httpshttps://api.mokapos.com/docs#tag/Modifier-Sales\n\n#### Discount Sales\n```python\nreport = x.Report\nreport.show_discount_sales(\n    outlet_id=1,\n    per_page=10,\n)\n```\nReference: https://api.mokapos.com/docs#tag/Discount-Sales\n\n#### Tax Sales\n```python\nreport = x.Report\nreport.show_tax_sales(\n    outlet_id=1,\n    per_page=10,\n)\n```\nReference: https://api.mokapos.com/docs#tag/Tax-Sales',
    'author': 'LandX Engineering',
    'author_email': 'tech@landx.id',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/landx-id/moka-python-sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
