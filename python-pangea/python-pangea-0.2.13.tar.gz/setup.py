# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pangea', 'pangea.services']

package_data = \
{'': ['*']}

install_requires = \
['alive-progress>=2.4.1,<3.0.0',
 'cryptography==37.0.2',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'schema>=0.7.5,<0.8.0']

setup_kwargs = {
    'name': 'python-pangea',
    'version': '0.2.13',
    'description': 'Pangea API SDK',
    'long_description': '# Pangea python-sdk\n\n## Setup\n\n```\npip3 install python-pangea\n# or\npoetry add python-pangea\n```\n\n## Usage\n\n### Secure Audit Service - Log Data\n\n```\nimport os\nfrom pangea.config import PangeaConfig\nfrom pangea.services import Audit\n\n# Read your access token from an env variable\ntoken = os.getenv("PANGEA_TOKEN")\n\n# Read the Audit Config ID from an env variable,\n# required for tokens enabled for all services\nconfig_id = os.getenv("AUDIT_CONFIG_ID")\n\n# Create a Config object contain the Audit Config ID\nconfig = PangeaConfig(config_id=config_id)\n\n# Initialize an Audit instance using the config object\naudit = Audit(token, config=config)\n\n# Create test data\n# All input fields are listed, only `message` is required\nevent = {\n    "action": "reboot",\n    "actor": "villan",\n    "target": "world",\n    "status": "error",\n    "source": "test",\n    "old" : "on",\n    "new" : "restart",\n    "message": "despicable act prevented",\n}\n\nresponse = audit.log(event)\n\nprint(response.result)\n```\n\n### Secure Audit Service - Search Data\n\n```\nimport os\nfrom pangea.config import PangeaConfig\nfrom pangea.services import Audit\n\n# Read your access token from an env variable\ntoken = os.getenv("PANGEA_TOKEN")\n\n# Read the Audit Config ID from an env variable\nconfig_id = os.getenv("AUDIT_CONFIG_ID")\n\n# Create a Config object contain the Audit Config ID\nconfig = PangeaConfig(config_id=config_id)\n\n# Initialize an Audit instance using the config object\naudit = Audit(token, config=config)\n\n# Search for \'message\' containing \'reboot\'\n# filtered on \'source=test\', with 5 results per-page\nresponse = audit.search(\n        query="message:prevented",\n        limit=5\n    )\n\nif response.success:\n    print("Search Request ID:", response.request_id, "\\n")\n\n    print(\n        f"Found {response.result.count} event(s)",\n    )\n    for row in response.result.events:\n        print(f"{row.event.received_at}\\taction: {row.event.actor}\\taction: {row.event.action}\\ttarget: {row.event.target}\\tstatus: {row.event.status}\\tmessage: {row.event.message}")\n\nelse:\n    print("Search Failed:", response.code, response.status)\n```\n\n### Secure Audit Service - Integrity Tools\n\n#### Verify audit data\n\nYou can provide a single event (obtained from the PUC) or the result from a search call.\nIn the latter case, all the events are verified.\n\nVefify an existing audit log file, reads from stdin if no filename is provided.\n\n```\npython -m verify_audit [-f <filename>]\n```\n\n#### Bulk Download Audit Data\n\nDownload all audit logs for a given time range.\nDatetimes must be in ISO 8601 format.\nIntended for use with the deep_verify tool\n\n```\npython -m dump_audit <datetime_from> <datetime_to>\n```\n\n#### Perform Exhaustive Verification of Audit Data\n\nVerify Audit data. This script does additional checking for any deleted entries.\nUse the dump_audit tool to download the events and root to be verified.\n\n```\npython -m deep_verify -e <events file> -r <root file>\n```\n\n## Contributing\n\nCurrently, the setup scripts only have support for Mac/ZSH environments.\nFuture support is incoming.\n\nTo install our linters, simply run `./dev/setup_repo.sh`\nThese linters will run on every `git commit` operation.\n\n## Generate SDK Documentation\n\n### Overview\n\nThroughout the SDK, there are Python doc strings that serve as the source of our SDK docs.\n\nThe documentation pipeline here looks like:\n\n1. Write doc strings throughout your Python code. Please refer to existing doc strings as an example of what and how to document.\n1. Make your pull request.\n1. After the pull request is merged, go ahead and run the `parse_module.py` script to generate the JSON docs uses for rendering.\n1. Copy the output from `parse_module.py` and overwrite the existing `python_sdk.json` file in the docs repo. File is located in `platform/docs/openapi/python_sdk.json` in the Pangea monorepo. Save this and make a merge request to update the Python SDK docs in the Pangea monorepo.\n\n### Running the autogen sdk doc script\n\nMake sure you have all the dependencies installed. From the root of the `python-pangea` repo run:\n\n```shell\npoetry install\n```\n\nNow run the script\n\n```shell\npoetry run python parse_module.py\n```\n\nThat will output the script in the terminal. If you\'re on a mac, you can do\n\n```shell\npoetry run python parse_module.py | pbcopy\n```\n\nto copy the output from the script into your clipboard. At the moment, a bunch of stuff will be printed to the terminal if you pipe it to `pbcopy`, but the script still works and copies the output to your clipboard.\n',
    'author': 'Glenn Gallien',
    'author_email': 'glenn.gallien@pangea.cloud',
    'maintainer': None,
    'maintainer_email': None,
    'url': '',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
