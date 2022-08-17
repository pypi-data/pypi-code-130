from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='NumIM04',
  version='0.0.1',
  description='Numerical integration using methods like: Trapezoidal method, Simpson rule, Newton cotes method and Compound trapezoidal method ',
  url='',
  author='Emmanuel Martínez',
  author_email='',
  license='MIT', 
  classifiers=classifiers,
  keywords='numerical integration', 
  packages=find_packages(),
  install_requires=[''] 
)