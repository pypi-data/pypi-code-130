# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['freelanceapi', 'freelanceapi.sections']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'freelanceapi',
    'version': '0.2.0',
    'description': 'FreelanceAPI is a module for reading & evaluating export files from the Freelance control system.',
    'long_description': '# FreecomAPI\n\n[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)\n[![PyPI version](https://badge.fury.io/py/freelanceapi.svg)](https://badge.fury.io/py/freelanceapi)\n[![GitHub license](https://img.shields.io/github/license/DarkJumper/FreelanceAPI)](https://github.com/DarkJumper/FreelanceAPI/blob/main/LICENSE)\n\nWith the Freelance API an export file from the ABB Freelance control system can be evaluated.\n\n\n## Freelance Reader\n\nThe ```FreelanceReader``` is a context manager. Depending on the file extension it returns the correct object\n:warning: Only certain file endings are evaluated\n- PLC\n- PLE\n- CSV\n\n### FreelanceReader\n\n```\nfrom freelanceapi import FreelanceReader\n\nwith FreelanceReader("/User/test.csv") as file:\n    print(file)\n\noutput >> freelanceapi.FreelanceExportData.FreelanceCsvData object at 0x10e13eac0\n```\n\n## Freelance Exports\nThe Freelance Export class supports the functions.\n\n### complete_file\nThe data of the complete file is returned as a tuple.\n```\nfrom freelanceapi import FreelanceReader\n\nwith FreelanceReader("/User/test.csv") as file:\n    print(file.complete_file())\n\noutput >> (([Program-Generated File -- DO NOT MODIFY],),([DUMP_VERSION],2061,),([DUMP_FILETYPE],101,)......)\n```\n\n### extract_sections\nThe desired range must be specified as a string. Then the selected range is output as a tuple.\nIf a section occurs more than once in the file, it is expanded in the tuple.\n```\nfrom freelanceapi import FreelanceReader\n\nwith FreelanceReader("/User/test.csv") as file:\n    print(file.extract_sections("Project Comment"))\n    \noutput >> ((\'[BEGIN_PROJECTCOMMENT];0;\',),)\n```\nThe following areas are available for selection:\n- Project Comment\n- Node\n- HW2\n- Area\n- Header\n- Resorce Association\n- Hardware Manager\n- Hardware\n- OPC Connection\n- Connections\n- HD Text\n- HD\n- MSR\n- OPC Adressing\n- EAM Initialisation\n- EAM\n- Project Tree\n\n### Freelance Export UML\n```mermaid\nclassDiagram\n    class FreelanceExportData  {\n        <<abstract>>\n        +file_data: tuple[str]\n        +complete_file()\n        +extract_sections(section)\n    }\n    \n    class FreelanceReader  {\n        <<context manager>>\n    }\n    FreelanceReader o-- FreelanceExportData : creates\n    FreelanceExportData <|-- FreelancePlcData\n    FreelanceExportData <|-- FreelancePleData\n    FreelanceExportData <|-- FreelanceCsvData\n```\n\n\nIn this example, the complete range of field IO is output.\n\nThe following sections can be read out:\n- ProjectComment:\n- AreaDefinition:\n- ProjectHeader:\n- ResourceAssociation:\n- HardWareManager:\n- HW2:\n- OPCConn:\n- Conn:\n- HDTextList:\n- HD:\n- MSR:\n- OPCAdress:\n- EAMInit:\n- EAM:\n- Node:\n- Pbaum:\n\n### row_identifier \n\n## It provides:\n\nMeanings of the Dict Keys:\n- ID: Identification\n- RID: Row Identification\n- LEN: Length of Dataset\n- NA: Next element available\n- MP: Measuring point\n- MT: Module Type\n- ST: Short Text\n- LT: Long Text\n- AD: Area Definition\n- SB: Status Bit\n- VN: Variable Name\n- DT: Data Typ\n- VT: Variable Text\n- PI: Process image\n- EX: Exported Variable\n- VC: Variable(0) or Const (1)\n- FB: FBS Name\n- LB: Libary\n- DTMN: DTM Number\n- DTMC: DTM Config\n- QC: Quantity counter\n- FN: Function Name\n- CN: Channel Name\n- IO: Input or Output\n- UB: Used Byte\n- B: Bit\n- BL: Byte Length\n- C: Commend\n- AC: Area Char\n- LA: Length of Area Text\n- AN: Area Name\n\n## :warning: Developer Info\n\nAll keys that contain a ? cannot be assigned to a function.\n\n\n\n\n',
    'author': 'Peter Schwarz',
    'author_email': 'p.schwarz1994@outlook.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DarkJumper/FreelanceAPI',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10.0,<4.0.0',
}


setup(**setup_kwargs)
