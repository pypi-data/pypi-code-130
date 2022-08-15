from distutils.core import setup

from setuptools import find_packages

import ontoim_py


def get_readme():
    with open('README.md', encoding='utf-8') as readme_file:
        return readme_file.read()


setup(
    name='ontoim-py',
    version=ontoim_py.__version__,
    description=ontoim_py.__description__,
    long_description=get_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/luca-martinelli-09/ontoim-py',
    author=ontoim_py.__author__,
    author_email=ontoim_py.__email__,
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Natural Language :: English',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        # 'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='ontoim ontology italianontology rdf graph'.split(),
    packages=find_packages(exclude=['tests*']),
    data_files=[('', ['LICENSE'])],
    python_requires='>=3.7, <4',
    install_requires=['rdflib>=6.0.0', 'ontopia_py>=0.1.0'],
)
