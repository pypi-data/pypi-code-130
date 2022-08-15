from setuptools import setup
import setuptools

setup(
    name='mkdocs_zhcorrect',
    version='0.0.1',
    description='mkdocs with zh',
    long_description='nothing',
    author='chenzongwei',
    author_email='17695480342@163.com',

    url='https://github.com/chen-001/pure_ocean_breeze.git',
    install_requires=['jieba'],
    python_requires='>=3',
    license='MIT',
    packages=setuptools.find_packages(),
    requires=[]
)

