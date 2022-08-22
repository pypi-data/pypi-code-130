from importlib.machinery import SourceFileLoader

from setuptools import find_packages, setup

version = SourceFileLoader('version', 'facturapi/version.py').load_module()


with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name='facturapi-2.0',
    version=version.__version__,
    author='Daniel Hernandez',
    author_email='itservices@kea.mx',
    description='Facturapi API Client V2',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    package_data=dict(facturapi=['py.typed']),
    python_requires='>=3.6',
    install_requires=[
        'requests>=2.4,<2.26',
        'pydantic==1.8.2',
        'dataclasses>=0.7;python_version<"3.7"',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    zip_safe=False)
