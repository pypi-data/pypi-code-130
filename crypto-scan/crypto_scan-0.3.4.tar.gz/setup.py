from setuptools import setup, find_packages

setup(
    name='crypto_scan',
    version='0.3.4',
    packages=find_packages(exclude=['tests*']),
    license='none',
    description='Python SDK for query crypto data from various API services.',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    install_requires=['requests', 'web3', 'pandas', 'tenacity', 'swifter'],
    url='https://github.com/ENsu/crypto-scan',
    author='Ian Su',
    author_email='ian@ivcrypto.io'
)
