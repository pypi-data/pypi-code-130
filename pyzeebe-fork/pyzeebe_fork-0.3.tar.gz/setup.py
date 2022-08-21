from setuptools import setup, find_packages


setup(
    name='pyzeebe_fork',
    version='0.3',
    license='MIT',
    author="Shahin",
    author_email='mohamed.megid@gmail.com',
    packages=find_packages('pyzeebe_fork'),
    package_dir={'': 'pyzeebe_fork'},
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