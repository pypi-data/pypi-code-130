# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['protobuf_init']

package_data = \
{'': ['*']}

install_requires = \
['protobuf>=3.19.1']

entry_points = \
{'console_scripts': ['protoc-gen-init_python = protobuf_init.plugin:main']}

setup_kwargs = {
    'name': 'protobuf-init',
    'version': '0.1.1',
    'description': 'generate __init__.py files for protobuf projects',
    'long_description': "# protobuf-init\n\nTo install:\n\n```bash\npip install protobuf-init\n```\n\nThis package will create `__init__.py` files when compiling `*.proto` files. Optionally, it will create relative imports from generated `*_pb.py`, `*_pb_grpc.py`, and `*_grpc.py` files from `protobuf`, `grpcio`, and `grpclib` packages, respectively.\n\nUsing the `protos` folder of this project as an example, the following command will generate the contents of the `example` package, also in this project (assuming `grpcio-tools` is installed):\n\n```bash\nexport PROTO_PATH=./protos\nexport GEN_PATH=.\npython -m grpc_tools.protoc \\\n    --python_out=$GEN_PATH \\\n    --mypy_out=$GEN_PATH \\\n    --init_python_out=$GEN_PATH \\\n    --init_python_opt=imports=protobuf+grpcio+grpclib \\\n    --grpc_python_out=$GEN_PATH \\\n    --grpclib_python_out=$GEN_PATH \\\n    --proto_path=$PROTO_PATH \n    $(find $PROTO_PATH -name '*.proto')\n```\n\nThe `--init_python_out=$GEN_PATH` flag indicates to call the plugin to create the init files.\n\nThe `--init_python_opt=imports=protobuf+grpcio+grpclib` indicates which relative imports to include in the init files. Allowed options are `protobuf`, `grpcio`, `grpclib`, separated by `+`. (Note that both grpcio and grpclib generate `<ServiceName>Stub` objects which would collide in the init file.)",
    'author': 'flynn',
    'author_email': 'crf204@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/crflynn/protobuf-init',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
