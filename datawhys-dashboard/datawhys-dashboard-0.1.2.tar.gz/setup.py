# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datawhys_dashboard', 'datawhys_dashboard.api']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.1.5,<2.0.0', 'requests>=2.27.0,<3.0.0']

setup_kwargs = {
    'name': 'datawhys-dashboard',
    'version': '0.1.2',
    'description': 'DataWhys Dashboard SDK allows users to create a DataWhys Dashboard directly within their Python notebooks',
    'long_description': '# DataWhys Dashboard Python SDK\n\nDataWhys Dashboard SDK allows users to create a DataWhys Dashboard directly within their Python notebooks.\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install datawhys-dashboard.\n\n```bash\npip install datawhys-dashboard\n```\n\n## Usage\n\n```python\nimport datawhys_dashboard as dwdash\n\n# Set your credentials\ndwdash.api_key = "<API_KEY>" # Ask your datawhys rep for this key\n\n# Your API key is stack specific. The SDK defaults to the main US stack, but you can\n# change this by setting `api_base` as follows. Ask your datawhys rep for the api base.\ndwdash.api_base = "https://<DOMAIN>/api/v0.2/"\n\n# Build a pandas dataframe and store in `df` (not shown)\n\n# Create a dashboard\nfrom datawhys_dashboard import create_dashboard\ncreate_dashboard(df, outcome="Risk")\n```\n\n## Contributing\n\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Take a look at `CONTRIBUTING.md` for more info\n\nPlease make sure to update tests as appropriate.\n\n## License\n\n[MIT](https://choosealicense.com/licenses/mit/)\n',
    'author': 'DataWhys DevTeam',
    'author_email': 'devteam@datawhys.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://datawhys.ai',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
