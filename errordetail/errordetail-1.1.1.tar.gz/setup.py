from setuptools import find_packages, setup

name = 'errordetail'

setup(
    name=name,
    version='1.1.1',
    author="Jayson",
    author_email='jaysonteng@163.com',
    description="encapsulate logger",
    python_requires=">=3.*.*",
    packages=find_packages(),
    package_data={"": ["*"]},  # 数据文件全部打包
    include_package_data=True,  # 自动包含受版本控制(svn/git)的数据文件
    zip_safe=False,
)

"""
python setup.py sdist bdist_wheel
pip install twine
twine upload dist/*
"""