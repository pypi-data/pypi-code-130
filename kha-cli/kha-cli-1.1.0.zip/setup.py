import os
from setuptools import find_packages, setup

import kha


_root = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(_root, 'README.md')) as f:
    readme = f.read()


setup(
    name='kha-cli',
    version=kha.__version__,
    py_modules=['kha-cli'],
    description='kha',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='khahux',
    author_email='khahux@gmail.com',
    install_requires=['click==8.1.3'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'kha = kha.cli:cli',
        ],
    }
)
