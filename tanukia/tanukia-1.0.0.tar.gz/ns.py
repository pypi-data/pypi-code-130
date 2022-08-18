#python setup.py sdist bdist_wheel
#python -m twine upload dist/*
from setuptools import setup, find_packages

setup(name='tanukia', # 패키지 명

version='1.0.0',

description='히토미 검색 라이브러리',
      
long_description="히토미 검색 라이브러리입니다.",
      
author='VoidAsMad',

author_email='voidasmad@gmail.com',

url='https://github.com/VoidAsMad/tanukia',

license='MIT', # MIT에서 정한 표준 라이센스 따른다

py_modules=['random'], # 패키지에 포함되는 모듈

python_requires='>=3',

install_requires=[], # 패키지 사용을 위해 필요한 추가 설치 패키지

packages=['tanukia'] # 패키지가 들어있는 폴더들

)