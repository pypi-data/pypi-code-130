from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 6 - Mature',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'Natural Language :: Spanish',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3.9',
  'Topic :: Scientific/Engineering :: Mathematics'
]
 
setup(
  name='NumIntM',
  version='0.0.2',
  description='Numerical integration using methods like: Trapezoidal method, Simpson rule, Newton cotes method and Compound trapezoidal method ',long_description=open('README.txt').read(),
  url='',
  author='Emmanuel Martínez',
  author_email='',
  license='MIT', 
  classifiers=classifiers,
  keywords='numerical integration aproximation', 
  packages=find_packages(),
  install_requires=[''] 
)