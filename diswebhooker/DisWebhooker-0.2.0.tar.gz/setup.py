from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  "Intended Audience :: Developers",
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'Operating System :: POSIX',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]


setup(
  name='DisWebhooker',
  version='0.2.0',
  description="this libray for webhooks. to have fun bots and to create discord applications.",
  long_description=open('README.md').read()+"\n\n\n"+open("CHANGELOG.txt").read(),
  long_description_content_type='text/markdown',
  url='',  
  author='Alawi Hussein Adnan Al Sayegh',
  author_email='programming.laboratorys@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='DisWebhooker,webhooker,diswebhook,webbot,webhook,discord,webdiscord',
  packages=find_packages(),
  install_requires=['mkrTree']
)