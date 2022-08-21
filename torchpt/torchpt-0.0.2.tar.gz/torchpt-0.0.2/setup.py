import os

from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

version = "0.0.2"#open('VERSION').read().strip()

def parse_requirements(fpath):
    packages = []
    with open(fpath, 'r') as f:
        for line in f.readlines():
            packages.append(line)

    return packages

setup(
    name='torchpt',
    version=version,
    packages=find_packages('checkpointing'), #["qct_monai_detection"],#
    # package_dir={'': 'checkpointing'},
    include_package_data=True,
    license='MIT',
    description='Unified model state dict and architecture checkpoints utils.',
    long_description=README,
    url='https://github.com/souvik3333/Checkpointing',
    author='Souvik Mandal',
    author_email='mandalsouvik76@gmail.com',
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ]
)
