"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

import pathlib
import re

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()  # current path
long_description = (here / 'README.md').read_text(encoding='utf-8')  # Get the long description from the README file
with open(here / 'requirements.txt') as fp:  # read requirements.txt
    install_reqs = [r.rstrip() for r in fp.readlines() if not r.startswith('#')]


def get_version():
    file = here / 'realtimecv/__init__.py'
    return re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', file.read_text(), re.M).group(1)


setup(
    name='yolocv',  # Required https://packaging.python.org/specifications/core-metadata/#name
    version=get_version(),  # Required https://packaging.python.org/en/latest/single_source_version.html
    description='realtimecv Python package',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional
    url='https://github.com/AyushExel/realtimecv',  # Optional, project's main homepage
    author='Ayush Chaurasia',  # Optional, name or the name of the organization which owns the project
    author_email='ayush.chaurarsia@gmail.com',  # Optional
    classifiers=['Development Status :: 5 - Production/Stable',  # 3 - Alpha, 4 - Beta, 5 - Production/Stable
                 'Intended Audience :: Developers',  # Indicate who your project is intended for
                 'Operating System :: OS Independent',  # Operation system
                 'Topic :: Education',  # Topics
                 'Topic :: Scientific/Engineering',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'Topic :: Scientific/Engineering :: Image Recognition',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',  # Pick your license as you wish
                 'Programming Language :: Python :: 3.7',  # Python version support
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9',
                 ],  # Classifiers help users find your project by categorizing it https://pypi.org/classifiers/
    keywords='machine-learning, deep-learning, ml, pytorch' , # Optional
    package_dir={'': 'realtimecv'},  # Optional, use if source code is in a subdirectory under the project root, i.e. `realtimecv/`
    packages=find_packages(where='realtimecv'),  # Required
    package_data={"realtimecv": ["py.typed"]},
    python_requires='>=3.7, <4',

    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=install_reqs,  # Optional, additional pip packeges to be installed by this pacakge installation

    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example: $ pip install sampleproject[dev]
    # Similar to `install_requires` above, these must be valid existing projects
    extras_require={'dev': ['check-manifest'],
                    'test': ['coverage'],
                    },  # Optional
    include_package_data=True
)
