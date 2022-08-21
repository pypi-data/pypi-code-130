from setuptools import setup, find_packages


setup(
    name='pyzeebe-fork',
    version='0.2',
    license='MIT',
    author="Shahin",
    author_email='mohamed.megid@gmail.com',
    packages=find_packages('pyzeebe'),
    package_dir={'': 'pyzeebe'},
    url='https://github.com/shahin84/pyzeebe',
    keywords='pyzeebe',
    install_requires=[
          'oauthlib',
          'requests-oauthlib',
          'zeebe-grpc',
          'aiofiles',
          'pytest'
      ],

)