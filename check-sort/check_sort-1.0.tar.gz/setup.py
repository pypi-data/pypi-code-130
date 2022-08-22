from distutils.core import setup
import setuptools

packages = ['check_sort']  # 唯一的包名
setup(name='check_sort',
      version='1.0',
      author='zengqi',
      packages=packages,
      package_dir={'requests': 'requests'}, )
