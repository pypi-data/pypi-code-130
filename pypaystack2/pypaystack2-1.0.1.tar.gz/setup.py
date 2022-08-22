# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypaystack2', 'pypaystack2.api']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.0,<3.0.0']

setup_kwargs = {
    'name': 'pypaystack2',
    'version': '1.0.1',
    'description': 'A fork of PyPaystack. A simple python wrapper for Paystack API.',
    'long_description': '# PyPaystack2\n\nA fork of [PyPaystack](https://github.com/edwardpopoola/pypaystack). A simple python wrapper for Paystack API. Checkout [Documentation](https://gray-adeyi.github.io/pypaystack2/)\n\n## Installation\n\n1. Create your [Paystack account](https://paystack.com/) to get your Authorization key that is required to use this package.\n2. Store your authorization key in your environment variable as `PAYSTACK_AUTHORIZATION_KEY` or pass it into the pypaystack api wrappers at instantiation.\n3. Install pypaystack2 package.\n\n```bash\npip install -U pypaystack2\n```\n\n## What\'s Pypaystack2\n\nSo Paystack provides RESTful API endpoints for developers from different platforms\nto integrate their services into their projects. So for python developers, to use\nthis endpoints, you might opt for a package like `requests` to handle all the\nAPI calls which involves a lot of boilerplate. Pypaystack2 abstracts this process\nby handling all this complexities under the hood and exposing simple APIs for\nyour python project. for example\n\n```python\n   from pypaystack2.api import Miscellaneous # assumes you have installed pypaystack2\n   from pypaystack2.utils import Country\n   miscellaneous_wrapper = Miscellaneous() # assumes that your paystack auth key is in \n   # your enviromental variables i.e PAYSTACK_AUTHORIZATION_KEY=your_key otherwise instatiate \n   # the Miscellaneous API wrapper as it is done below.\n   # miscellaneous_wrapper = Miscellaneous(auth_key=your_paystack_auth_key)\n   response = miscellaneous_wrapper.get_banks(country=Country.NIGERIA,use_cursor=False) # Requires internet connection.\n   print(response)\n```\n\nWith the code snippet above, you have successfully queried Paystack\'s Miscellaneous API\nto get a list of banks supported by paystack. A `requests` equivalent of the above will\nbe like\n\n```python\n   import requests # assumes you have requests installed.\n   headers = {\n      "Content-Type":"application/json",\n      "Authorization": "Bearer <your_auth_key>"\n      }\n   paystack_url = \'https://api.paystack.co/bank?perPage=50&country=ng&use_cursor=false\'\n   response = requests.get(paystack_url,headers=headers) # requires internet connection\n   print(response.json())\n```\n\nWhile both approaches achieve the same goal, `pypaystack2` uses `requests` under the hood and\nmanages the headers and URL routes to endpoints so you can focus more on the actions. with the `miscellaneous_wrapper`\nin the example above. you can call all endpoints associated with the Miscellaneous API with methods\nprovided like `.get_banks`, `.get_providers`, `.get_countries` and `.get_states`.\n\nPypaystack2 provides wrappers to all of Paystack APIs in its `pypaystack2.api` subpackage.\neach of the wrappers are classes named to closely match the Paystack API. so say you want\nto use Paystack\'s Invoices API, you\'d  import the wrapper with `from pypaystack2.api import Invoice`\nfor the Invoices API. All endpoints available on the Invoices API are available as methods\nin the `Invoice` wrapper. Say you wanted to create an invoice by sending a\n`POST` request to Paystack\'s Invoice API endpoint `/paymentrequest`, you\'ll call\n`Invoice` wrapper\'s `.create` method.\n\n```python\n   from pypaystack2.api import Invoice\n   invoice_wrapper = Invoice()\n   response = invoice_wrapper.create(customer="CUS_xwaj0txjryg393b",amount=10000) # Creates an invoice with a charge of ₦100\n   print(response)\n```\n\nFrom here you can check out the tutorials section to get more examples and get familiar or surf the\ndocumentation for wrappers and methods you\'ll need for your next project. Hurray!\n[Documentation](https://gray-adeyi.github.io/pypaystack2/)\n',
    'author': 'Gbenga Adeyi',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
