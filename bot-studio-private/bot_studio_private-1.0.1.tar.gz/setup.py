import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
VERSION = '1.0.1'
PACKAGE_NAME = 'bot_studio_private'
AUTHOR = 'DataKund'
AUTHOR_EMAIL = 'datakund@gmail.com'
URL = 'https://github.com/you/your_package'
LICENSE = 'Apache License 2.0'
DESCRIPTION = 'Automation Library'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'requests','tqdm'
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages(),
      package_dir={'bot_studio_private': 'bot_studio_private'},
      package_data={'bot_studio_private': ['DataKund.exe']},
      entry_points={
        'console_scripts': [
            'datakund = bot_studio_private.dk_studio:main',
        ],}
      )