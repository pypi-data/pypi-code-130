# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qutrunk',
 'qutrunk.backends',
 'qutrunk.backends.ibm',
 'qutrunk.circuit',
 'qutrunk.circuit.gates',
 'qutrunk.circuit.ops',
 'qutrunk.converters',
 'qutrunk.dagcircuit',
 'qutrunk.example',
 'qutrunk.qasm',
 'qutrunk.qasm.node',
 'qutrunk.sim',
 'qutrunk.sim.local',
 'qutrunk.sim.local.pybind11',
 'qutrunk.sim.local.pybind11.docs',
 'qutrunk.sim.local.pybind11.pybind11',
 'qutrunk.sim.local.pybind11.tests',
 'qutrunk.sim.local.pybind11.tests.extra_python_package',
 'qutrunk.sim.local.pybind11.tests.extra_setuptools',
 'qutrunk.sim.local.pybind11.tests.test_cmake_build',
 'qutrunk.sim.local.pybind11.tests.test_embed',
 'qutrunk.sim.local.pybind11.tools',
 'qutrunk.sim.qusprout',
 'qutrunk.sim.qusprout.code',
 'qutrunk.sim.qusprout.qusprout',
 'qutrunk.sim.qusprout.qusproutdata',
 'qutrunk.sim.qusprout.work',
 'qutrunk.test',
 'qutrunk.test.gate',
 'qutrunk.tools',
 'qutrunk.visualizations']

package_data = \
{'': ['*'],
 'qutrunk': ['config/*',
             'doc/distribute_package.md',
             'doc/distribute_package.md',
             'doc/project_documentation.md',
             'doc/project_documentation.md'],
 'qutrunk.qasm': ['libs/*'],
 'qutrunk.sim': ['Release/*',
                 'local/QuEST/*',
                 'local/QuEST/include/*',
                 'local/QuEST/src/*',
                 'local/QuEST/src/CPU/*',
                 'local/QuEST/src/GPU/*',
                 'local/pybind11/docs/_static/*',
                 'local/pybind11/docs/advanced/*',
                 'local/pybind11/docs/advanced/cast/*',
                 'local/pybind11/docs/advanced/pycpp/*',
                 'local/pybind11/docs/cmake/*',
                 'local/pybind11/include/pybind11/*',
                 'local/pybind11/include/pybind11/detail/*',
                 'local/pybind11/include/pybind11/stl/*',
                 'local/pybind11/tests/test_cmake_build/installed_embed/*',
                 'local/pybind11/tests/test_cmake_build/installed_function/*',
                 'local/pybind11/tests/test_cmake_build/installed_target/*',
                 'local/pybind11/tests/test_cmake_build/subdirectory_embed/*',
                 'local/pybind11/tests/test_cmake_build/subdirectory_function/*',
                 'local/pybind11/tests/test_cmake_build/subdirectory_target/*']}

install_requires = \
['networkx>=2.8,<3.0',
 'numba>=0.56.0,<0.57.0',
 'numpy>=1.22.3,<2.0.0',
 'ply>=3.11,<4.0',
 'pyyaml>=6.0,<7.0',
 'requests>=2.27.1,<3.0.0',
 'retworkx>=0.11.0,<0.12.0',
 'thrift>=0.15.0,<0.16.0']

setup_kwargs = {
    'name': 'qutrunk',
    'version': '0.1.9',
    'description': 'qutrunk is an open source library for quantum computing.',
    'long_description': '## qutrunk\nqutrunk is an quantum programming framework developed by QuDoor corporation, provide the required APIs for quantum programming, it works as follow: \n\nExport quantum programs based on quantum circuit, qubit and quantum gate, etc. Then you can run the \nquantum circuit by the following two ways:\n1. Use PC for quantum computing(work as the default way). \n2. Connect with QuBox(a quantum device developed by qudoor), to run quantum programs, it provide more powerful quantum computing. \n\n## Install\n1. Install from whl package, run the following command directly:\n```\npip install qutrunk\n```\n\n2. Install from source code, run the following command to install qutrunk by source code:\n```\npython3 setup.py install\n```\n\n## Example:\nbell-pair quantum algorithm：\n\n```\nfrom qutrunk.circuit import QCircuit\nfrom qutrunk.circuit.gates import H, CNOT, Measure\n\nqc = QCircuit()\nqr = qc.allocate(2) # allocate\n\nH | qr[0]   # apply gate\nCNOT | (qr[0], qr[1])\nMeasure | qr[0]\nMeasure | qr[1]\n\nqc.print(qc)   # print circuit\nres = qc.run(shots=1024) # run circuit\nprint(res.get_counts()) # print result\n```\n\n ## License\n Apache Licence 2.0\n\n Copyright (c) 2022-2025 By QUDOOR Technolgies Inc. All Right Reserved.',
    'author': 'qudoorzh2022',
    'author_email': 'qudoorzh2022@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://www.qudoor.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
