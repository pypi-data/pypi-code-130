from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='timerdecor',
  version='0.1.1',
  description='Timer Decorator for Python',
  long_description=open('README.txt').read(),
  url='https://github.com/alpheay/TimerDecor',  
  author='Sagnik Nandi',
  author_email='nik.nandi.1@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='arrays', 
  packages=find_packages(),
  install_requires=[''] 
)