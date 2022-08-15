
from distutils.core import setup
setup(
  name = 'safpy',         
  packages = ['safpy'],   
  version = '0.1',      
  license='MIT',        
  description = 'Python library to work with SAF files',   
  author = 'Dogukan Karatas',                   
  author_email = 'karatasdogukan@gmail.com',      
  url = 'https://github.com/dogukankaratas/safpy',   
  download_url = 'https://github.com/dogukankaratas/safpy/archive/refs/tags/0.1.tar.gz',   
  install_requires=[            
          'pandas',
          'cmath'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',     
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3.7'
  ],
)