from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='Wifi_Checker',
  version='0.0.2',
  description='A easy wifi checker // Un semplice verificatore di connesione',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='IlProgrammatore.py',
  author_email='asciart2008@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='Wifi_Checker', 
  packages=find_packages(),
  install_requires=['requests'] 
)