from setuptools import setup, find_packages

requires=[
	'attrs==22.1.0',
	'Automat==20.2.0',
	'certifi==2022.6.15',
	'cffi==1.15.1',
	'charset-normalizer==2.1.0',
	'constantly==15.1.0',
	'cryptography==37.0.4',
	'cssselect==1.1.0',
	'et-xmlfile==1.1.0',
	'fake-useragent==0.1.11',
	'Faker==13.15.1',
	'filelock==3.8.0',
	'hyperlink==21.0.0',
	'idna==3.3',
	'incremental==21.3.0',
	'itemadapter==0.7.0',
	'itemloaders==1.0.4',
	'jmespath==1.0.1',
	'lxml==4.9.1',
	'numpy==1.23.1',
	'openpyxl==3.0.10',
	'parsel==1.6.0',
	'Protego==0.2.1',
	'pyasn1==0.4.8',
	'pyasn1-modules==0.2.8',
	'pycparser==2.21',
	'PyDispatcher==2.0.5',
	'pyOpenSSL==22.0.0',
	'python-dateutil==2.8.2',
	'queuelib==1.6.2',
	'requests==2.28.1',
	'requests-file==1.5.1',
	'Scrapy==2.6.2',
	'scrapy-fake-useragent==1.4.4',
	'service-identity==21.1.0',
	'six==1.16.0',
	'tldextract==3.3.1',
	'Twisted==22.4.0',
	'twisted-iocpsupport==1.0.2',
	'typing_extensions==4.3.0',
	'urllib3==1.26.11',
	'w3lib==1.22.0',
	'zope.interface==5.4.0',
    ]



setup(
    name='clutch.co-scraper',
    version='1.0.0',
    author='Maksym Remezovskyi',
    author_email='maks.remezovskij1@gmail.com',
    description=("clutch.co-scraper is a command-line application written in Python"
                 " that scrapes and saves information about firms according to the user-defined filters."),
    url='https://github.com/maksr137/clutch.co-scraper',
    packages=find_packages(),
    install_requires=requires,
    entry_points = {
       'console_scripts': [
           'clutch.co-scraper=clutch_co_scraper.clutch_co_scraper.spiders.main:run_spider'
       ]
    },
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)