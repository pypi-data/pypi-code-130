# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 14:57:02 2022

@author: Richie Bao-caDesign设计(cadesign.cn)
"""
from setuptools import setup,find_packages,find_namespace_packages

setup(name='toolkit4beginner', #应用名，即包名
      version='0.1', #版本号
      license="BSD", #版权声明
      author='Richie Bao-caDesign设计(cadesign.cn)', #作者名
      author_email='richiebao@outlook.com', #作者邮箱
      description='模块、包和分发文件目录组织结构说明', #描述
      url='https://richiebao.github.io/USDA_CH_final',  #项目主页    
      packages=find_packages(),#包括安装包内的python包；find_namespace_packages()，和find_packages()
      python_requires='>=3.6', #pyton版本控制
      platforms='any',
      install_requires=['matplotlib','statistics','numpy'] #自动安装依赖包（库）
      )