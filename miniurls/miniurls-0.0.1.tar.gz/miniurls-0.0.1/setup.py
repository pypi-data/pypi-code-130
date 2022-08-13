from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name='miniurls',
  version='0.0.1',
  author="Hero",
  long_description=long_description,
  long_description_content_type='text/markdown',
  packages=find_packages('src'),
  package_dir={'': 'src'},
  url='https://github.com/heromr/miniurls',
  keywords=[
      'miniurls'
      'miniurl'
      'miniurlpy'
      'heromr'
      'short link'
      'shortener'
      'short'
      'short url'
      'url shortener'
  ],
  install_requires=[],
)
