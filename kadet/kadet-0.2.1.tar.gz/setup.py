# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kadet']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1',
 'pydantic>=1.9.2,<2.0.0',
 'python-box==6.0.2',
 'typeguard>=2.12.1']

setup_kwargs = {
    'name': 'kadet',
    'version': '0.2.1',
    'description': 'Easily define and reuse complex Python objects that serialize into JSON or YAML.',
    'long_description': '# kadet\n\nEasily define and reuse complex Python objects that serialize into JSON or YAML.\n\n![GitHub Workflow Status](https://img.shields.io/github/workflow/status/kapicorp/kadet/Python%20lint%20and%20tests)\n\n## Example\n\n```python\nfrom kadet import BaseObj\nfrom pprint import pprint\n\nships = BaseObj()\nships.root.type.container = ["panamax", "suezmax", "post-panamax"]\nships.root.type.carrier = ["conventional", "geared", "gearless"]\nships.root.type.tanker = BaseObj.from_yaml("tankers.yml")\n\npprint(ships.root)\n\n# output\n{\'type\': {\'carrier\': [\'conventional\',\n                      \'geared\',\n                      \'gearless\'],\n          \'container\': [\'panamax\',\n                        \'suezmax\',\n                        \'post-panamax\'],\n          \'tanker\': [\'oil\', \'liquified-gas\', \'chemical\']}}\n```\n\n## Installation\n\nInstall using `pip install kadet`.\n\n## Overview\n\n### BaseObj\n\nBaseObj implements the basic object that serializes into JSON or YAML.\nSetting keys in `self.root` means they will be serialized. Keys can be set as an hierarchy of attributes.\n\nThe `self.body()` method is reserved for setting self.root on instantiation.\n\nThe example below:\n\n```python\nclass MyApp(BaseObj):\n  def body(self):\n    self.root.name = "myapp"\n    self.root.inner.foo = "bar"\n    self.root.list = [1, 2, 3]\n\nyaml.dump(MyApp().dump())\n```\n\nserializes into:\n\n```yaml\n---\nname: myapp\ninner:\n  foo: bar\nlist:\n  - 1\n  - 2\n  - 3\n```\n\nThe `self.new()` method can be used to define a basic constructor.\n\n`self.need()` checks if a key is set and errors if it isn\'t (with an optional custom error message).\n`self.optional()` sets a key as optional. Use `default` keyword to set default value when not set.\n\nBoth `self.new()` and `self.body()` method accept the `istype` keyword to validate value type on runtime.\nSupports `typing` types.\n\n`kwargs` that are passed onto a new instance of BaseObj are always accessible via `self.kwargs`\n\n`self.new_with()` is an utility method to call `super().new()` while passing kwargs to the super class.\n\nIn this example, MyApp needs `name` and `foo` to be passed as kwargs.\n\n```python\nclass MyApp(BaseObj):\n  def new(self):\n    self.need("name")\n    self.need("foo", msg="please provide a value for foo")\n    self.optional("baz")\n\n  def body(self):\n    self.root.name = self.kwargs.name\n    self.root.inner.foo = self.kwargs.foo\n    self.root.list = [1, 2, 3]\n\nobj = MyApp(name="myapp", foo="bar")\n```\n\n### Setting a skeleton\n\nDefining a large body with Python can be quite hard and repetitive to read and write.\n\nThe `self.root_file()` method allows importing a YAML/JSON file to set `self.root`.\n\nMyApp\'s skeleton can be set instead like this:\n\n```yaml\n#skel.yml\n---\nname: myapp\ninner:\n  foo: bar\nlist:\n  - 1\n  - 2\n  - 3\n```\n\n```python\nclass MyApp(BaseObj):\n  def new(self):\n    self.need("name")\n    self.need("foo", msg="please provide a value for foo")\n    self.root_file("path/to/skel.yml")\n```\n\nExtending a MyApp\'s skeleton is possible just by implementing `self.body()`:\n\n```python\nclass MyApp(BaseObj):\n  def new(self):\n    self.need("name")\n    self.need("foo", msg="please provide a value for foo")\n    self.root_file("path/to/skel.yml")\n\n  def body(self):\n    self.set_replicas()\n    self.root.metadata.labels = {"app": "mylabel"}\n\n  def set_replicas(self):\n    self.root.spec.replicas = 5\n```\n\n### Inheritance\n\nPython inheritance will work as expected:\n\n```python\n\nclass MyOtherApp(MyApp):\n  def new(self):\n    super().new()  # MyApp\'s new()\n    self.need("size")\n\n  def body(self):\n    super().body()  #  we want to extend MyApp\'s body\n    self.root.size = self.kwargs.size\n    del self.root.list  # get rid of "list"\n\nobj = MyOtherApp(name="otherapp1", foo="bar2", size=3)\nyaml.dump(obj.dump())\n```\nserializes to:\n\n```yaml\n---\nname: otherapp1\ninner:\n  foo: bar2\nreplicas: 5\nsize: 3\n```\n\n### BaseModel\n\nBaseModel integrates Kadet semantics with [Pydantic](https://github.com/pydantic/pydantic)\'s BaseModel together with powerful data validation and type hinting features.\nJust like in BaseObj, keys in `self.root` will be serialized, but kwargs is no longer necessary as BaseModel\'s parameters are set as attributes in `self`.\n\nThe `self.body()` method is reserved for setting self.root on instantiation.\n\nThe example below:\n\n```python\nclass Boat(BaseModel):\n  name: str  # Required\n  length: int  # Required\n  description: str = "I am a boat"  # Default description\n\n  def body(self):\n    self.root.name = self.name\n    self.root.details.length = self.length\n    self.root.details.description = self.description\n\nprint(yaml.dump(Boat(name="Boaty", length=600).dump()))\n\n---\ndetails:\n  description: I am a boat\n  length: 600\nname: Boaty\n```\n',
    'author': 'Ricardo Amaro',
    'author_email': 'ramaro@kapicorp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kapicorp/kadet',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
