import io
from os.path import abspath, dirname, join
from setuptools import find_packages, setup


HERE = dirname(abspath(__file__))
LOAD_TEXT = lambda name: io.open(join(HERE, name), encoding='UTF-8').read()
DESCRIPTION = '\n\n'.join(LOAD_TEXT(_) for _ in [
    'README.rst'
])

setup(
  name = 'revalorise',      
  packages = ['revalorise'], 
  version = '0.0.3', 
  license='MIT', 
  description = 'Who is Revalorise',
  long_description=DESCRIPTION,
  author = 'Revalorise',                 
  author_email = 'Blackball007b@gmail.com',     
  url = 'https://github.com/Revalorise/Revalorise_package',  
  download_url = 'https://github.com/Revalorise/Revalorise_package.git',  
  keywords = ['Revalorise', 'Introduction'],
  classifiers=[
    'Development Status :: 3 - Alpha',     
    'Intended Audience :: Education',     
    'Topic :: Utilities',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
  ],
)