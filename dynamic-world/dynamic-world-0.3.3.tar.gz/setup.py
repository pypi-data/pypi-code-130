# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dynamic_world']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'earthengine-api>=0.1.316,<0.2.0',
 'geedim>=1.2.0,<2.0.0',
 'geemap>=0.15.3,<0.16.0',
 'geojson>=2.5.0,<3.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'typer>=0.5.0,<0.6.0']

setup_kwargs = {
    'name': 'dynamic-world',
    'version': '0.3.3',
    'description': 'Land-use land-cover analysis using Dynamic World App from Earth Engine',
    'long_description': '# dynamic-world 🛰️\n\nWrapper package around [Google\'s Dynamic World App](https://dynamicworld.app/) [^1], to easily monitor forests and calculate their co2 storage on a near-real time.\n\n[^1]: This dataset is produced for the Dynamic World Project by Google in partnership with National Geographic Society and the World Resources Institute.\n\n## Install\n\n```zsh\npip install dynamic-world\n```\n\n## Usage\n\nGiven a Forest (defined as a directory with some configuration files, see bellow), this package retrieves statistics and images of it.\nSee [Jupyter tutorial](Notebooks/dynamic_world_tutorial.ipynb) for a usage example.\n\n### Forests\n\nEach forest (or "proyect") is defined inside a directory with a given name and 2 files:\n\n1. A forest_config.yml (name is mandatory) which looks like this:\n\n```yaml\n# Name of the forest/proyect\nname: Sample\n\n# Locations of the geojson file\ngeojson: \'./sample.geojson\'\n\n# Co2 factor: how many tons of CO2 are stored on average per hectare\nco2_factor: {\n    \'trees\': 591.85,\n    \'grass\': 6,\n    \'bare\': 6,\n    \'crops\': 11.5,\n    \'flooded_vegetation\': 6,\n    \'other\': 0,\n    \'factor_pixel\': 100, # Indicates how many pixels are (on average) inside a hectare\n  }\n\n# Date in which the reforestation started, in format YYYY-mm-dd\nstart_date: \'2022-01-01\'\n```\n\n2. A valid geojson file [see](https://geojson.org/) (named as defined in forest_config.yml) that defines the area\n\nInternally, forests are stored as a ForestConfig instance (see dynamic_world.configurations for more details).\n\n### Available calculations\n\nGiven a forest and a pair of dates, we download the forest\'s landcover image, landcover statistics and total CO2 calculation. In other words, we mean the amount of CO2 (measured in tons) that a forest stores (and therefore is not released into the atmosphere if it was burned :D)\n\nThe forest image is stored as a [Cloud Optimized Geotiff](https://www.cogeo.org/) file. The expression used for the file-name is the following:\n\n```python\nf"{forest.name.replace(\' \', \'_\')}_{start_date}_{end_date}.cog.tif"\n```\n\nFor [reductions](https://developers.google.com/earth-engine/guides/reducers_intro) we use the Mode (polling). If a very large time interval is specified, recent changes in the forest will be masked by old pixel values. It is encouraged to use the smallest possible time intervals (at least a week is required or there may not be data). However, depending on some factors (such as the amount of clouds), specifying a small time interval may result in many NA (see mrv.calculations documentation for further info on how NA are treated when calculating the co2 factor).\n\n---\n\n# Development notes\n\nWe encourage developers to open the repository using [VSCode remote container functionality](https://code.visualstudio.com/docs/remote/containers).\n\n## How to run tests locally\n\n- to test run \'pytest\' in the root directory of the proyect\n- to run coverage use \'pytest --cov mrv --cov-branch --cov-report term-missing --disable-warnings\'\n\n## How to run tests in docker\n\n```zsh\n# Build test docker\ndocker build --tag dw --file Dockerfile --target dev .\n\n# Run lint and tests\ndocker run dw /bin/bash -c "flake8 && pytest"\n```\n',
    'author': 'Reforestum team',
    'author_email': 'info@reforestum.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://reforestum.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
