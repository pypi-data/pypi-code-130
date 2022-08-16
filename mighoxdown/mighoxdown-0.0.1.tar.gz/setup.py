from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='mighoxdown',
  version='0.0.1',
  description='This Package can download from social media sites',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  long_description_content_type='text/markdown',
  url='',  
  author='Migho Ahmed',
  author_email='migho.ahmed@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='Youtube , SoundCloud , migho , instagram , tool , pypi', 
  packages=find_packages(),
  install_requires=['requests'] 
)
