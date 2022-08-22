from setuptools import setup, find_packages

from os import path
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='olcarpc',
    version='0.0.2',
    description='A Python gRPC client library for openLCA.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/GreenDelta/olcarpc.py',
    packages=find_packages(exclude=[
        "tests", "*.tests", "*.tests.*", "tests.*", "examples"]),
    install_requires=['grpcio>=1.47.0', 'protobuf>=3.20.1'],
    keywords=['openLCA', 'life cycle assessment', 'LCA'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
    ]
)
