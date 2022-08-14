from setuptools import setup
# from distutils.core import setup
def diao_res():
      with open("README.rst",encoding='utf-8') as rf:
            return rf.read()
setup(name='famokuai',version='1.0.1'
      ,description='this is a niubi lib gcytfgugy'
      ,author='lizhi',author_email='1249705133@qq.com'
      ,packages=['famokuai'],py_modules=['tool'],
      long_description=diao_res(),license="MIT"
      )