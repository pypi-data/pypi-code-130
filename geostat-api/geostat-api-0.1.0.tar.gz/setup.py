from setuptools import setup, find_packages


def version():
    import importlib
    mod = importlib.import_module('geostat_api')
    return mod.__version__


def readme():
    with open('README.md') as f:
        return f.read()


def requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()


setup(
    name='geostat-api',
    author='Mirko Mälicke',
    author_email='mirko@hydrocode.de',
    version=version(),
    description='A OGC api compliant REST API for geostatistical applications by hydrocode',
    long_description=readme(),
    long_description_content_type='text/markdown',
    install_requires=requirements(),
    packages=find_packages(),
    licence='GPLv3',
)