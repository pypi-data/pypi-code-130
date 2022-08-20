from distutils.core import setup
from setuptools import find_packages

with open("README.md", "r") as f:
    long_description = f.read() or "create requests from yapi api doc"

setup(name='yapi2requests',  # 包名
      version='0.1.0',  # 版本号
      description='create requests from yapi api doc',
      long_description=long_description,
      author='yiyao',
      author_email='dengjiajie0109@gmail.com',
      url='https://github.com/SEtester',
      install_requires=[
          "loguru>=0.6.0"
      ],
      license='Apache License 2.0',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Topic :: Software Development :: Libraries'
      ],
      )
