from distutils.core import setup
from setuptools import find_packages

with open("README.rst", "r") as f:
    long_description = f.read()

setup(name='sqlite_lee_tools',  # 包名
      version='1.0.0',  # 版本号
      description='A small tool for sqlite',
      long_description=long_description,
      author='lee7goal',
      url='https://github.com/Lee7goal',
      author_email='lee7goal@qq.com',
      install_requires=['loguru', 'sqlite3'],
      license='MIT License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Topic :: Software Development :: Libraries'
      ],
      )
