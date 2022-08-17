from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: OS Independent',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='proxy-ninja',
  version='0.1.0',
  description='Python3 library for scraping http/https and socks(4) proxies.',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.md').read(),
  long_description_content_type="text/markdown",
  url='https://github.com/sc4rfurry/ProxyNinja---PyPi',  
  author='sc4rfurry',
  author_email='akalucifr@protonmail.ch',
  license='MIT', 
  classifiers=classifiers,
  keywords=['proxy', 'free proxy', 'proxy grabber', 'http proxy', 'https proxy', 'socks proxy', 'socks4 proxy', 'socks5 proxy'],
  packages=find_packages(),
  install_requires=[
'selenium',
'selenium-stealth',
'rich'] 
)
