# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ahio', 'ahio.drivers']

package_data = \
{'': ['*']}

install_requires = \
['pymodbus3>=1.0.0,<2.0.0', 'pyserial>=3.5,<4.0', 'python-snap7>=1.1,<2.0']

setup_kwargs = {
    'name': 'ahio',
    'version': '1.0.26',
    'description': 'I/O Communication Library',
    'long_description': "ahio\n====\n\nahio is a communication library whose goal\nis to abstract the interfacing with various I/O hardwares, so that changing\nhardware becomes possible with minimum code modification. It's desired that\nan application that already works with an I/O hardware will only need pin\nremapping and possibly initial setup change to work with another hardware, not\nentire code rewrite.\n\nIt works with drivers, which are installed in the `ahio.drivers` package. Every\ndriver must implement the API described in the `ahio.abstract_driver` package.\nIf you plan to use this library or develop a driver, read the documentation\nthere.\n\n\nInstallation\n------------\n\nSimplest way is to use pip: `pip3 install ahio`\nAlternatively you can checkout this repository and run\n`python3 setup.py install`\n\n\nBasic usage\n-----------\n\n```python\n# Import the package:\nimport ahio\n\n# You can see what drivers are available in this platform by calling\nprint(ahio.list_available_drivers())\n\n# Instantiate the desired driver\nwith ahio.new_driver('Arduino') as arduino:\n  # The driver can have a driver-specific setup function. Call it as/if needed.\n  arduino.setup('/dev/tty.usbmodem1421')\n\n  # Map the pins. From now on, when you use 1 in the API, it will have effects\n  # on pin D3 in the Arduino. If you change hardware in the future, just change\n  # the mapping.\n  arduino.map_pin(1, arduino.Pins.D3)\n  arduino.map_pin(2, arduino.Pins.D13)\n  arduino.map_pin(3, arduino.Pins.A1)\n\n  # Change a pin direction (Input or Output)\n  arduino.set_pin_direction([1, 2], ahio.Direction.Output)\n  arduino.set_pin_direction(3, ahio.Direction.Input)\n\n  # Set the output of a pin\n  arduino.write([1, 2], ahio.LogicValue.High)\n  arduino.write(1, 0.4, pwm=True)\n\n  # Read the input of a pin\n  print(arduino.read(3))\n```\n\nDocumentation\n-------------\n\nDocumentation is hosted at [GitHub](https://acristoffers.github.io/ahio)\n",
    'author': 'Álan Crístoffer',
    'author_email': 'acristoffers@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/acristoffers/ahio',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
