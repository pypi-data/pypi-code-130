from setuptools import setup, find_packages


setup(
    name='covey-sdk',
    version='0.0.1',
    license='MIT',
    author="Vadim Serebrinskiy",
    author_email="vs@covey.io",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/covey-io/ethereum-contract-interaction',
    keywords='covey',
    install_requires=[
            'eth_account==0.6.1',
            'eth_keys==0.4.0',
            'nest_asyncio==1.5.5',
            'pandas==1.4.2',
            'pyparsing==3.0.9',
            'python-dotenv==0.20.0',
            'pytz==2022.1',
            'requests==2.28.0',
            'web3==6.0.0b3',
      ],

)