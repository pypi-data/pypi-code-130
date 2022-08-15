from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='covey-sdk',
    version='0.0.3',
    license='MIT',
    author="Vadim Serebrinskiy",
    author_email="vs@covey.io",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data = True,
    url='https://github.com/covey-io/ethereum-contract-interaction',
    keywords='covey',
    install_requires=[
            'alpaca_trade_api==2.2.0',
            'eth_account==0.6.1',
            'eth_keys==0.4.0',
            'nest_asyncio==1.5.5',
            'pandas==1.4.2',
            'pyparsing==3.0.9',
            'pytz==2022.1',
            'requests==2.28.0',
            'setuptools==58.1.0',
            'web3==6.0.0b3',
      ],

)