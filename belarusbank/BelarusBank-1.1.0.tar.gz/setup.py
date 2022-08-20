from setuptools import setup


long_description = """
# BelarusBankAPI
> Оболочка для использования BelarusBankAPI на Python
---
### Quick Start
```commandline
from BelarusBank import BelBankAPI

def main(city: str):
    bank = BelBankAPI()
    print(bank.get_infobox(city))

if __name__ == '__main__':
    main('Минск')
```
---
### Asyncio Method
```commandline
import asyncio
from BelarusBank import AIOBelBankAPI

async def main(city: str):
    bank = AIOBelBankAPI()
    gems = await bank.get_gems(city)
    print(gems)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main('Гродно'))
```
_[by BARL](https://t.me/barltg)_
"""


setup(name='BelarusBank',
      version='1.1.0',
      author='Barl',
      description='Оболочка для использования BelarusBankAPI на Python',
      packages=['BelarusBank'],
      author_email='adwer197@gmail.com',
      classifiers=[
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires=[
          'requests',
          'aiohttp',
          'fake-useragent'
      ],
      zip_safe=False)
