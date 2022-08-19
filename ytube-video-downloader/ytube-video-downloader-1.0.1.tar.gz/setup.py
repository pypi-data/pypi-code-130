from setuptools import setup, find_packages

requires = [
    'aiohttp==3.8.1',
    'aiosignal==1.2.0',
    'async-timeout==4.0.2',
    'attrs==22.1.0',
    'cachetools==5.2.0',
    'certifi==2022.6.15',
    'charset-normalizer==2.1.0',
    'fake-useragent==0.1.11',
    'frozenlist==1.3.1',
    'google-api-core==2.8.2',
    'google-api-python-client==2.57.0',
    'google-auth==2.10.0',
    'google-auth-httplib2==0.1.0',
    'googleapis-common-protos==1.56.4',
    'httplib2==0.20.4',
    'idna==3.3',
    'multidict==6.0.2',
    'protobuf==4.21.5',
    'pyasn1==0.4.8',
    'pyasn1-modules==0.2.8',
    'pyparsing==3.0.9',
    'requests==2.28.1',
    'rsa==4.9',
    'six==1.16.0',
    'uritemplate==4.1.1',
    'urllib3==1.26.11',
    'yarl==1.8.1',
]

setup(
    name='ytube-video-downloader',
    version='1.0.1',
    author='Maksym Remezovskyi',
    author_email='maks.remezovskij1@gmail.com',
    description=('YTube-Video-Downloader is a command-line application written in Python that downloads videos from a specific YouTube channel according to given filters.'),
    url='https://github.com/maksr137/ytube-video-downloader',
    packages=find_packages(),
    install_requires=requires,
    entry_points = {
        'console_scripts': [
            'ytube-video-downloader=ytube_video_downloader.main:main'
        ]
    },
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)