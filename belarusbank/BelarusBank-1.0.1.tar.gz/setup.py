from setuptools import setup

long_description = '''
__Quick Start__

```commandline
from BelarusBank import BelBankAPI


def main(city: str):
    bank = BelBankAPI()
    print(bank.get_infobox(city))


if __name__ == '__main__':
    main('Минск')
```'''

setup(name='BelarusBank',
      version='1.0.1',
      author='Barl',
      description='Оболочка для использования BelarusBankAPI на Python',
      packages=['BelarusBank'],
      author_email='adwer197@gmail.com',
      classifiers=[
          "Programming Language :: Python :: 3.7",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires=[
          'requests',
          'fake-useragent'
      ],
      zip_safe=False)

