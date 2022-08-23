# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tracarbon',
 'tracarbon.cli',
 'tracarbon.emissions',
 'tracarbon.exporters',
 'tracarbon.hardwares',
 'tracarbon.hardwares.data',
 'tracarbon.locations',
 'tracarbon.locations.data']

package_data = \
{'': ['*']}

install_requires = \
['aiocache>=0.11.1,<0.12.0',
 'aiohttp>=3.8.1,<4.0.0',
 'ec2-metadata>=2.10.0,<3.0.0',
 'loguru>=0.6.0,<0.7.0',
 'msgpack>=1.0.4,<2.0.0',
 'psutil>=5.9.1,<6.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'typer>=0.4.1,<0.7.0',
 'ujson>=5.3.0,<6.0.0']

extras_require = \
{'datadog': ['datadog>=0.44.0,<0.45.0']}

entry_points = \
{'console_scripts': ['tracarbon = tracarbon.cli:main']}

setup_kwargs = {
    'name': 'tracarbon',
    'version': '0.2.4',
    'description': "Tracarbon is a Python library that tracks your device's energy consumption and calculates your carbon emissions.",
    'long_description': '![Alt text](logo.png?raw=true "Tracarbon logo")\n\n[![doc](https://img.shields.io/badge/docs-python-blue.svg?style=flat-square)](https://fvaleye.github.io/tracarbon)\n[![pypi](https://img.shields.io/pypi/v/tracarbon.svg?style=flat-square)](https://pypi.org/project/tracarbon/)\n![example workflow](https://github.com/fvaleye/tracarbon/actions/workflows/build.yml/badge.svg)\n\n\n## 📌 Overview\nTracarbon is a Python library that tracks your device\'s energy consumption and calculates your carbon emissions.\n\nIt detects your location and your device automatically before starting to export measurements to an exporter. \nIt could be used as a CLI with already defined metrics or programmatically with the API by defining the metrics that you want to have.\n\nRead more in this [article](https://medium.com/@florian.valeye/tracarbon-track-your-devices-carbon-footprint-fb051fcc9009).\n\n## 📦 Where to get it\n\n```sh\n# Install Tracarbon\npip install tracarbon\n```\n\n```sh\n# Install one or more exporters from the list\npip install \'tracarbon[datadog]\'\n```\n\n### 🔌 Devices: energy consumption\n| **Devices** |                                **Description**                                 |\n|-------------|:------------------------------------------------------------------------------:|\n| **Mac**     | ✅ Global energy consumption of your Mac (must be plugged into a wall adapter). |\n| **Linux**   |                             ❌ Not yet implemented.                             |\n| **Windows** |                             ❌ Not yet implemented.                             |\n\n| **Cloud Provider** |                                                                                               **Description**                                                                                               |\n|--------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|\n| **AWS**            | ✅ Used the CPU usage with the EC2 instances carbon emissions datasets of [cloud-carbon-coefficients](https://github.com/cloud-carbon-footprint/cloud-carbon-coefficients/blob/main/data/aws-instances.csv). |\n| **GCP**            |                                                                                           ❌ Not yet implemented.                                                                                            |\n| **Azure**          |                                                                                           ❌ Not yet implemented.                                                                                            |\n\n\n## 📡 Exporters\n| **Exporter** |       **Description**        |\n|--------------|:----------------------------:|\n| **Stdout**   | Print the metrics in Stdout. |\n| **Datadog**  | Send the metrics to Datadog. |\n\n### 🗺️ Locations\n| **Location** |                                         **Description**                                          | **Source**                                                                                                                                                    |\n|--------------|:------------------------------------------------------------------------------------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------|\n| **Europe**   | Static file of the European Environment Agency Emission for the co2g/kwh for European countries. | [EEA website](https://www.eea.europa.eu/data-and-maps/daviz/co2-emission-intensity-9#tab-googlechartid_googlechartid_googlechartid_googlechartid_chart_11111) |\n| **France**   |               Get the co2g/kwh in near real-time using the RTE energy consumption.               | [RTE API](https://opendata.reseaux-energies.fr)                                                                                                               |\n| **AWS**      |                 Static file of the AWS Grid emissions factors.                 | [cloud-carbon-coefficients](https://github.com/cloud-carbon-footprint/cloud-carbon-coefficients/blob/main/data/grid-emissions-factors-aws.csv)                |\n\n### ⚙️ Configuration\n| **Parameter**                     | **Description**                                                                |\n|-----------------------------------|:-------------------------------------------------------------------------------|\n| **TRACARBON_API_ACTIVATED**       | The activation of the real-time data collection of the carbon emission factor. |\n| **TRACARBON_METRIC_PREFIX_NAME**  | The prefix to use in all the metrics name.                                     |\n| **TRACARBON_INTERVAL_IN_SECONDS** | The interval in seconds to wait between the metrics evaluation.                |\n| **TRACARBON_LOG_LEVEL**        | The level to use for displaying the logs.                                      |\n\n\n## 🔎 Usage\n\n**Command Line**\n```sh\ntracarbon run Stdout\n```\n\n**API**\n```python\nfrom tracarbon import CarbonEmission\nfrom tracarbon.exporters import Metric, StdoutExporter\n\nmetric = Metric(\n    name="co2_emission",\n    value=CarbonEmission().run,\n    tags=[],\n)\nexporter = StdoutExporter(metrics=[metric])\nexporter.start()\n# Your code\nexporter.stop()\n\nwith exporter:\n    # Your code\n```\n\n## 💻 Development\n\n**Local: using Poetry**\n```sh\nmake setup\nmake unit-test\n```\n\n## 🛡️ Licence\n[Apache License 2.0](https://raw.githubusercontent.com/fvaleye/tracarbon/main/LICENSE.txt)\n\n## 📚 Documentation\nThe documentation is hosted here: https://fvaleye.github.io/tracarbon/documentation\n',
    'author': 'Florian Valeye',
    'author_email': 'fvaleye@github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
