from setuptools import setup, find_packages
from HPCC_bitcoin_parser import __version__


setup(
    name='HPCC_bitcoin_parser',
    version=__version__,
    packages=find_packages(),
    url='https://github.com/Invictus-ill/HPCC_blockchain_parser.git',
    author='Rohan Maheshwari',
    author_email='therohanm@gmail.com',
    description='Bitcoin blockchain parser',
    test_suite='HPCC_bitcoin_parser.tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=[
        'python-bitcoinlib==0.11.0',
        'plyvel==1.2.0'
    ]
)
