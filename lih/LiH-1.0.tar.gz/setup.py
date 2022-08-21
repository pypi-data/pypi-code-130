from setuptools import setup

setup(
    
    name='LiH',# 需要打包的名字,即本模块要发布的名字
    
    version='v1.0',#版本
    
    description='This package is for getting started with mathematical modeling', # 简要描述
    
    py_modules=['LiH'],   #  需要打包的模块
    
    author='Tan Xin', # 作者名
    
    author_email='1792733991@qq.com',   # 作者邮件
    
    url='https://github.com/Jack-TanXin/LIH', # 项目地址,一般是代码托管的网站
    
    # requires=['requests','urllib3'], # 依赖包,如果没有,可以不要
    license='MIT'
    
)