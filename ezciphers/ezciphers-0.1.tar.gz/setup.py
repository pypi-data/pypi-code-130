from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 3 - Alpha',
  'Intended Audience :: Developers',
  'Operating System :: OS Independent',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='ezciphers',
  version='0.1',
  description='a set of basic ciphers, e.g. atbash or rot13.',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Tyler Carrothers',
  author_email='itxhazrd@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='cipher', 
  packages=find_packages(),
  install_requires=[''] 
)