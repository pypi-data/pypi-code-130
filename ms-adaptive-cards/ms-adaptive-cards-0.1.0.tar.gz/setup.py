# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['msadaptivecards']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0', 'pyhumps>=3.7.2,<4.0.0']

setup_kwargs = {
    'name': 'ms-adaptive-cards',
    'version': '0.1.0',
    'description': 'Python implementation of Microsoft Adaptive Cards',
    'long_description': '<a name="readme-top"></a>\n\n[![Contributors][contributors-shield]][contributors-url]\n[![Forks][forks-shield]][forks-url]\n[![Stargazers][stars-shield]][stars-url]\n[![Issues][issues-shield]][issues-url]\n[![MIT License][license-shield]][license-url]\n<!--[![LinkedIn][linkedin-shield]][linkedin-url]-->\n\n<!-- PROJECT LOGO -->\n<br />\n<div align="center">\n  <a href="https://github.com/idarb-oss/adaptive-cards">\n    <img src="docs/assets/adaptive-card.svg" alt="Logo" width="80" height="80">\n  </a>\n\n<h3 align="center">ms-adaptive-cards</h3>\n\n  <p align="center">\n    Implements Microsoft Adaptive Cards models to generate json data from Python.\n    <br />\n    <a href="https://github.com/idarb-oss/adaptive-cards"><strong>Explore the docs »</strong></a>\n    <br />\n    <br />\n    <a href="https://github.com/idarb-oss/adaptive-cards/issues">Report Bug</a>\n    ·\n    <a href="https://github.com/idarb-oss/adaptive-cards/issues">Request Feature</a>\n  </p>\n</div>\n\n\n\n<!-- TABLE OF CONTENTS -->\n<details>\n  <summary>Table of Contents</summary>\n  <ol>\n    <li>\n      <a href="#about-the-project">About The Project</a>\n      <ul>\n        <li><a href="#built-with">Built With</a></li>\n      </ul>\n    </li>\n    <li>\n      <a href="#getting-started">Getting Started</a>\n      <ul>\n        <li><a href="#prerequisites">Prerequisites</a></li>\n        <li><a href="#installation">Installation</a></li>\n      </ul>\n    </li>\n    <li><a href="#usage">Usage</a></li>\n    <li><a href="#roadmap">Roadmap</a></li>\n    <li><a href="#contributing">Contributing</a></li>\n    <li><a href="#license">License</a></li>\n  </ol>\n</details>\n\n\n\n## About The Project\n\nPython implementation to create [adaptive cards](https://adaptivecards.io/) as specified from Microsoft.\n\n<p align="right">(<a href="#readme-top">back to top</a>)</p>\n\n\n\n### Built With\n\n- [`Python`](https://python.org)\n- [`pydantic`](https://pydantic.com) for data model modeling\n\n<p align="right">(<a href="#readme-top">back to top</a>)</p>\n\n\n## Getting Started\n\nThis is an [Adaptive Cards](https://adaptivecards.io/) implementation to generate json structures according to the specification from Microsoft.\n\n\n### Prerequisites\n\nThis is an example of how to list things you need to use the software and how to install them.\n\n\n### Installation\n\n- poetry\n\n  ```sh\n  poetry add adaptive-cards\n  ```\n\n- pip\n\n  ```sh\n  pip install adaptive-cards\n  ```\n\n<p align="right">(<a href="#readme-top">back to top</a>)</p>\n\n\n## Usage\n\nUse this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.\n\n_For more examples, please refer to the [Documentation](https://example.com)_\n\n<p align="right">(<a href="#readme-top">back to top</a>)</p>\n\n\n\n## Roadmap\n\n- Card Elements\n  - [x] TextBlock\n  - [ ] Image\n  - [ ] Media\n  - [ ] MediaSource\n  - [ ] RichTextBlock\n  - [ ] TextRun\n- Containers\n  - [ ] ActionSet\n  - [x] Container\n  - [x] ColumnSet\n  - [x] Column\n  - [ ] FactSet\n  - [ ] Fact\n  - [ ] ImageSet\n  - [x] Table\n  - [x] TableCell\n- [ ] Actions\n  - [ ] ShowCard\n  - [ ] ToggleVisibility\n  - [ ] TargetElement\n  - [ ] Execute\n- [ ] Types\n  - [ ] Refersh\n  - [ ] Authentication\n  - [ ] TokenExchangeResource\n  - [ ] AuthCardButton\n\nSee the [open issues](https://github.com/idarb-oss/adaptive-cards/issues) for a full list of proposed features (and known issues).\n\n<p align="right">(<a href="#readme-top">back to top</a>)</p>\n\n\n\n## Contributing\n\nContributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.\n\nIf you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".\nDon\'t forget to give the project a star! Thanks again!\n\n1. Fork the Project\n2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)\n3. Commit your Changes (`git commit -m \'Add some AmazingFeature\'`)\n4. Push to the Branch (`git push origin feature/AmazingFeature`)\n5. Open a Pull Request\n\n<p align="right">(<a href="#readme-top">back to top</a>)</p>\n\n\n\n## License\n\nDistributed under the MIT License. See `LICENSE.txt` for more information.\n\n<p align="right">(<a href="#readme-top">back to top</a>)</p>\n\n\n\n<!-- MARKDOWN LINKS & IMAGES -->\n<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->\n[contributors-shield]: https://img.shields.io/github/contributors/idarb-oss/adaptive-cards.svg?style=for-the-badge\n[contributors-url]: https://github.com/idarb-oss/adaptive-cards/graphs/contributors\n[forks-shield]: https://img.shields.io/github/forks/idarb-oss/adaptive-cards.svg?style=for-the-badge\n[forks-url]: https://github.com/idarb-oss/adaptive-cards/network/members\n[stars-shield]: https://img.shields.io/github/stars/idarb-oss/adaptive-cards.svg?style=for-the-badge\n[stars-url]: https://github.com/idarb-oss/adaptive-cards/stargazers\n[issues-shield]: https://img.shields.io/github/issues/idarb-oss/adaptive-cards.svg?style=for-the-badge\n[issues-url]: https://github.com/idarb-oss/adaptive-cards/issues\n[license-shield]: https://img.shields.io/github/license/idarb-oss/adaptive-cards.svg?style=for-the-badge\n[license-url]: https://github.com/idarb-oss/adaptive-cards/blob/master/LICENSE.txt\n[product-screenshot]: images/screenshot.png\n[AdaptiveCards]: https://adaptivecards.io/explorer/AdaptiveCard.html\n',
    'author': 'Idar Bergli',
    'author_email': 'idarb@pm.me',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
