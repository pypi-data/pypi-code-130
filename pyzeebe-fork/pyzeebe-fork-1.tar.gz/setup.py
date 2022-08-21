# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyzeebe',
 'pyzeebe.channel',
 'pyzeebe.client',
 'pyzeebe.errors',
 'pyzeebe.function_tools',
 'pyzeebe.grpc_internals',
 'pyzeebe.job',
 'pyzeebe.task',
 'pyzeebe.worker']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.7,<0.9',
 'oauthlib>=3.1.0,<3.2.0',
 'requests-oauthlib>=1.3.0,<1.4.0',
 'zeebe-grpc>=1.2.0,<2.0.0']

setup_kwargs = {
    'name': 'pyzeebe-fork',
    'version': '1',
    'description': 'Zeebe client api',
    'long_description': '# Pyzeebe\n\npyzeebe is a python grpc client for Zeebe.\n\nZeebe version support:\n\n| Pyzeebe version | Tested Zeebe versions  |\n| :-------------: | ---------------------- |\n|      3.x.x      | 1.0.0                  |\n|      2.x.x      | 0.23, 0.24, 0.25, 0.26 |\n|      1.x.x      | 0.23, 0.24             |\n\n## Getting Started\n\nTo install:\n\n`pip install pyzeebe`\n\nFor full documentation please visit: https://pyzeebe.readthedocs.io/en/stable/\n\n## Usage\n\n### Worker\n\nThe `ZeebeWorker` class gets jobs from the gateway and runs them.\n\n```python\nimport asyncio\n\nfrom pyzeebe import ZeebeWorker, Job, create_insecure_channel\n\n\nchannel = create_insecure_channel(hostname="localhost", port=26500) # Create grpc channel\nworker = ZeebeWorker(channel) # Create a zeebe worker\n\n\nasync def on_error(exception: Exception, job: Job):\n    """\n    on_error will be called when the task fails\n    """\n    print(exception)\n    await job.set_error_status(f"Failed to handle job {job}. Error: {str(exception)}")\n\n\n@worker.task(task_type="example", exception_handler=on_error)\ndef example_task(input: str) -> dict:\n    return {"output": f"Hello world, {input}!"}\n\n\n@worker.task(task_type="example2", exception_handler=on_error)\nasync def another_example_task(name: str) -> dict: # Tasks can also be async\n    return {"output": f"Hello world, {name} from async task!"}\n\nloop = asyncio.get_running_loop()\nloop.run_until_complete(worker.work()) # Now every time that a task with type `example` or `example2` is called, the corresponding function will be called\n```\n\nStop a worker:\n\n```python\nawait zeebe_worker.stop() # Stops worker after all running jobs have been completed\n```\n\n### Client\n\n```python\nfrom pyzeebe import ZeebeClient, create_insecure_channel\n\n# Create a zeebe client\nchannel = create_insecure_channel(hostname="localhost", port=26500)\nzeebe_client = ZeebeClient(channel)\n\n# Run a Zeebe process instance\nprocess_instance_key = await zeebe_client.run_process(bpmn_process_id="My zeebe process", variables={})\n\n# Run a process and receive the result\nprocess_instance_key, process_result = await zeebe_client.run_process_with_result(\n    bpmn_process_id="My zeebe process",\n    timeout=10000\n)\n\n# Deploy a BPMN process definition\nawait zeebe_client.deploy_process("process.bpmn")\n\n# Cancel a running process\nawait zeebe_client.cancel_process_instance(process_instance_key=12345)\n\n# Publish message\nawait zeebe_client.publish_message(name="message_name", correlation_key="some_id")\n\n```\n\n## Tests\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install pyzeebe\n\n`pytest tests/unit`\n\n## Contributing\n\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\nPlease make sure to update tests as appropriate.\n\n## Versioning\n\nWe use [SemVer](semver.org) for versioning. For the versions available, see the tags on this repository.\n\nIn order to bump the current version run:\n\n```shell\n$ bump2version <part>\n```\n\nwhere part is the part that will be bumped (major/minor/patch/rc).\n\nThis will bump the version in all relevant files as well as create a git commit.\n\n## License\n\nWe use the MIT license, see [LICENSE.md](LICENSE.md) for details\n',
    'author': 'Mohamed',
    'author_email': 'mohamed.shahin@nana.sa',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/WhatsLab/pyzebee',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
