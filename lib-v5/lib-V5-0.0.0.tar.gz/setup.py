import setuptools

setuptools.setup(
    name='lib-V5',
    version='0.0.0',
    description='Local packages for development',

    author='hypothesisbase',
    author_email="support@hypothesisbase.com",
    url= 'http://pypi.python.org/pypi/lib-V5/0.0.0',
    license="MIT",

    install_requires=[
        "bs4",
        "leveldb",
        "selenium",
    ],
    packages=setuptools.find_packages(),
    zip_safe=False
)
