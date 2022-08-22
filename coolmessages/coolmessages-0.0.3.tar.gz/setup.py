from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 3 - Alpha',
  'Intended Audience :: Developers',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='coolmessages',
  version='0.0.3',
  description='Enhance your terminal with cool and unnecessary messages 😏',
  long_description_content_type='text/markdown',
  long_description=open('README.md', encoding="utf-8").read(),
  url='https://github.com/anonymouscoolguy/coolmessages',  
  author='anonymouscoolguy',
  author_email='anonymouscoolguy69@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords=['cool messages', 'terminal', 'terminal messages', 'ascii', 'ascii messages'], 
  packages=find_packages(),
  install_requires=[''] 
)