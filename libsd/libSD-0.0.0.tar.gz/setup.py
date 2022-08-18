import setuptools

pkg_name = 'libSD'
version = '0.0.0'

setuptools.setup(
    name=pkg_name,
    version=version,
    description='Local packages for development',

    author='hypothesisbase',
    author_email="support@hypothesisbase.com",
    url= f'http://pypi.python.org/pypi/{pkg_name}/{version}',
    license="MIT",

    install_requires=[
        "bs4",
        "leveldb",
        "selenium",
        "paramiko",
        "setuptools",
    ],
    packages=setuptools.find_packages(),
    zip_safe=False
)
