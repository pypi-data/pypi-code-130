# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['media_filesize_estimator']

package_data = \
{'': ['*']}

install_requires = \
['defusedxml>=0.7.1,<0.8.0',
 'matplotlib>=3.5.3,<4.0.0',
 'pymediainfo>=5.1.0,<6.0.0',
 'rich>=10.14.0,<11.0.0',
 'typer[all]>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['media-filesize-estimator = '
                     'media_filesize_estimator.__main__:app']}

setup_kwargs = {
    'name': 'media-filesize-estimator',
    'version': '1.0.0',
    'description': 'Estimates media file size in different formats w/o actually converting the file',
    'long_description': '# media-filesize-estimator\n\n<div align="center">\n\n[![PYPI Version](https://img.shields.io/pypi/v/media-filesize-estimator.svg)](https://pypi.org/project/media-filesize-estimator/)\n[![Python Version](https://img.shields.io/pypi/pyversions/media-filesize-estimator.svg)](https://pypi.org/project/media-filesize-estimator/)\n[![Build status](https://github.com/kHarshit/media-filesize-estimator/workflows/build/badge.svg?branch=main&event=push)](https://github.com/kHarshit/media-filesize-estimator/actions?query=workflow%3Abuild)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/kHarshit/media-filesize-estimator/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n![Coverage Report](assets/images/coverage.svg)\n\nEstimates media file size in different formats w/o actually converting the file\n\n</div>\n\n\n## Installation\n\nThe package works with python 3.8+.\n\n```bash\npip install -U media-filesize-estimator\n\n# or install with `Poetry`\npoetry add media-filesize-estimator\n```\n\nThen you can run\n\n```bash\nmedia-filesize-estimator --help\n\n# or with `Poetry`:\npoetry run media-filesize-estimator --help\n```\n\n## Working\n\n```\n$ media-filesize-estimator --help\nUsage: media-filesize-estimator [OPTIONS]\n\n  Estimates media file size in different formats w/o actually converting the\n  file\n\nOptions:\n  -m, --media TEXT           Media file path  [required]\n  -p, --property TEXT        Parameter (resolution/frame_rate/bit_depth/sampli\n                             ng_rate/channels) to compare\n  -sf, --save-format TEXT    Format (json/xml/csv) to save media metadata\n  -sl, --save-location TEXT  Location to save media metadata and/or graph\n                             [default: ./]\n  -v, --version              Prints the version of the media-filesize-\n                             estimator package.\n  --help                     Show this message and exit.\n```\n\n```\n$ media-filesize-estimator --media assets/sample_video_redfort.mp4 --property resolution --save-location /tmp/ --save-format xml\nThe given media file is of type : video\nExtracting data from file : sample_video_redfort.mp4\nExtraction completed successfully to file : /tmp/sample_video_redfort.xml\nMetadata is saved at /tmp/sample_video_redfort.xml\nThe given media file is of type : video\nUncompressed file size estimation of the given file in MB with resolution 1920x1080 : 593.262 MB\nUncompressed file size estimation of the given file in MB with resolution 3840x2160 : 2373.047 MB\nUncompressed file size estimation of the given file in MB with resolution 2560x1440 : 1054.688 MB\nUncompressed file size estimation of the given file in MB with resolution 1920x1080 : 593.262 MB\nUncompressed file size estimation of the given file in MB with resolution 1280x720 : 263.672 MB\nUncompressed file size estimation of the given file in MB with resolution 640x360 : 65.918 MB\nPlotting the graph for the given parameter : resolution\nEstimated filesize graph saved at /tmp//estimated_filesize.png\n```\n\n## Contributing\n\nThanks for considering contributing to this project. Please follow [Contributing guidelines](https://github.com/kHarshit/media-filesize-estimator/blob/main/CONTRIBUTING.md).\n\n## 🛡 License\n\n[![License](https://img.shields.io/github/license/kHarshit/media-filesize-estimator)](https://github.com/kHarshit/media-filesize-estimator/blob/main/LICENSE)\n\nThis project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/kHarshit/media-filesize-estimator/blob/main/LICENSE) for more details.\n\n## 📃 Citation\n\n```bibtex\n@misc{media-filesize-estimator,\n  author = {kHarshit, Pappuru-Dinesh, TejodhayBonam, AbdulBasitA},\n  title = {Estimates media file size in different formats w/o actually converting the file},\n  year = {2022},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{https://github.com/kHarshit/media-filesize-estimator}}\n}\n```\n\n### Credits \n\nThis project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)\n',
    'author': 'kHarshit',
    'author_email': 'kumar_harshit@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kHarshit/media-filesize-estimator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
