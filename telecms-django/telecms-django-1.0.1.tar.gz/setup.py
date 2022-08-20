import os
from setuptools import setup, find_packages


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    try:
        file = open(path, encoding='utf-8')
    except TypeError:
        file = open(path)
    return file.read()


def get_install_requires():
    install_requires = [
        'Django',
        'requests',
        'telecms-bridge-base==1.0.1'
    ]

    try:
        from collections import OrderedDict
    except ImportError:
        install_requires.append('ordereddict')

    return install_requires

setup(
    name='telecms-django',
    version=__import__('telecms_django').VERSION,
    description='',
    long_description=read('README.rst'),
    author='Billy Truong',
    author_email='account@service.exchange',
    url='https://github.com/serviceexchange/telecms_bridge',
    packages=find_packages(),
    license='MIT',
    classifiers=[

    ],
    zip_safe=False,
    include_package_data=True,
    install_requires=get_install_requires()
)
