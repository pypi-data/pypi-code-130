# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['esovalue']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.1', 'gmpy', 'mistune>=2.0.3', 'mpmath']

setup_kwargs = {
    'name': 'esovalue',
    'version': '0.1.13',
    'description': 'Valuation of employee stock options',
    'long_description': '# ESO-value\nReceiving stock options from your company? Wondering what they are worth? ESO-value calculates the value of\nEmployee Stock Options based on the Hull-White model[1][2].\nThis library is used in the [ESO valuation app](https://eso.stephanethibaud.xyz/).\n\n## Installation\nRun `pip install esovalue`\n\n## Usage\n```python\nfrom esovalue.eso import value_eso\n\nvalue_eso(strike_price=50, stock_price=50, volatility=0.3, risk_free_rate=0.075,\n          dividend_rate=0.025, exit_rate=0.03, vesting_years=3, expiration_years=10, \n          iterations=1000, m=3)\n```\nDescription of the parameters:\n```\nstrike_price\t\t- Strike price\nstock_price\t\t- Current price of the underlying stock\niterations\t\t- More iterations is more precise but requires more memory/CPU\nrisk_free_rate\t\t- Risk-free interest rate\ndividend_rate\t\t- Dividend rate\nexit_rate\t\t- Employee exit rate (over a year)\nvesting_years\t\t- Vesting period (in years)\nexpiration_years\t- Years until expiration\nvolatility\t\t- Volatility (standard deviation on returns)\nm\t\t\t- Strike price multiplier for early exercise \n                          (exercise when the strike_price*m >= stock_price)\n```\n\n## References\n[1]: Hull, J, and White, A:  How to Value Employee Stock Options Financial Analysts Journal, Vol. 60, No. 1,\n    January/February 2004, 114-119.\\\n[2]: Hull, J. (2018). Options, Futures, and Other Derivatives (Global Edition).\n',
    'author': 'Stéphane Thibaud',
    'author_email': 'snthibaud@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/snthibaud/esovalue',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
