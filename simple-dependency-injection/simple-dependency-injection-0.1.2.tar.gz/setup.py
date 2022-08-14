# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simple_dependency_injection']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'simple-dependency-injection',
    'version': '0.1.2',
    'description': '',
    'long_description': '# simple-dependency-injection\n\nsimple-dependency-injection is a library is lightweight library to apply dependency injection pattern in a simple way.\n\n**Note:** simple-dependency-injection is in a development state, there were some checks to finish the first version\n\n## Install\n\nYou can install it through pip\n\n``pip install simple-dependency-injection``\n\n\n## Use\n\nTo use simple-dependency-injection only have to create a dependency container and register your dependencies.\n\nThe library check types of parameters and result, its important typing that.\n\nThat is an example of dependency container configuration\n\n```\nfrom abc import ABC, abstractmethod\n\nclass ConfigDependencyInterface(ABC):\n    @abstractmethod\n    def get_percent_benefit(self) -> float:\n        pass\n\nclass ConfigDependency(ConfigDependencyInterface):\n    def get_percent_benefit(self) -> float:\n        return 10.0\n   \ndef config_generator() -> ConfigDependencyInterface:\n    return ConfigDependency()\n\nclass ServiceInterface(ABC):\n    def __init__(self, config: ConfigDependencyInterface):\n        self.config = config\n\n    @abstractmethod\n    def calculate_benefit(self, amount: float) -> float:\n        pass\n\nclass Service(ServiceInterface):\n    def calculate_benefit(self, amount: float) -> float:\n        return amount * (self.config.get_percent_benefit() / 100)\n  \ndef service_generator(config: ConfigDependencyInterface) -> ServiceInterface:\n    return Service(config=config)\n\ndependency_container = DependencyContainer()\ndependency_container.register_dependency(\n    ConfigDependencyInterface, config_generator\n)\ndependency_container.register_dependency(\n    ServiceInterface, service_generator\n)\n```\n\nOnce the dependency container is created, you can use it with inject decorator.\n```\n@dependency_container.inject\ndef main(service: ServiceInterface):\n    service.calculate_benefit(10)\n\nmain()\n```\n\nOther way to use the dependency container is get the dependency directly\n```\ndependency_container.get_dependency(ServiceInterface).calculate_benefit(10)\n```\n\nFor testing is easy override dependencies\n```\nclass ConfigToTestDependency(ConfigDependencyInterface):\n    def get_percent_benefit(self) -> float:\n        return 0.0\n\ndef test_config_generator() -> ConfigDependencyInterface:\n    return ConfigToTestDependency()\n\nwith dependency_container.test_container() as dependency_container_test:\n    dependency_container_test.override(\n        ConfigDependencyInterface, test_config_generator\n    )\n    main()\n```\n',
    'author': 'AiAmEspanis',
    'author_email': 'rafaperez.software@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
