# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 14:57:02 2022

@author: Richie Bao-caDesign设计(cadesign.cn)
"""
from setuptools import setup,find_packages,find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='toolkit4beginner', #应用名，即包名
    version='0.3.3', #版本号
    license="MIT", #版权声明，BSD,MIT
    author='Richie Bao-caDesign设计(cadesign.cn)', #作者名
    author_email='richiebao@outlook.com', #作者邮箱
    description='模块、包和分发文件目录组织结构说明', #描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://richiebao.github.io/USDA_CH_final',  #项目主页 
    package_dir={"": "src"},
    packages=find_packages(where='src'),#包括安装包内的python包；find_namespace_packages()，和find_packages() ['toolkit4beginner']
    python_requires='>=3.6', #pyton版本控制
    platforms='any',
    install_requires=['matplotlib','statistics','numpy'] #自动安装依赖包（库）
    # include_package_data=True,
    # classifiers=[
    #   "Programming Language :: Python :: 3", #that you indicate whether you support Python 2, Python 3 or both.
    #    "License :: OSI Approved :: MIT License", #Pick your license as you wish (should match "license" above)
    #   "Operating System :: OS Independent", #运行的系统
    #   'Development Status :: 3 - Alpha', #How mature is this project? Common values are：3 - Alpha； 4 - Beta；5 - Production/Stable 
    #   ],      
      
      )