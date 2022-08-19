from setuptools import setup, find_packages
 
setup(name='telesave',
      version='0.1',
      url='',
      license='MIT',
      author='Whoamis',
      author_email='valonmean@mail.ru',
      description='Add static script_dir() method to Path',
      packages=find_packages(exclude=['telesave']),
      long_description=open('README.md').read(),
      zip_safe=False)