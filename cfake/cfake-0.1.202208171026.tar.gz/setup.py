from setuptools import setup
import datetime

with open("./README.md", "rb") as fh:
    long_description = fh.read()


def date_to_str(date=None, format_str="0.1.%Y%m%d%H%M"):
    if date is None:
        date = datetime.datetime.now()
    return date.strftime(format_str)


setup(
    name='cfake',
    version=date_to_str(),
    description='一个简单的测试数据生成器',
    author='hammer',
    author_email='liuzhuogood@foxmail.com',
    long_description=str(long_description, encoding='utf-8'),
    long_description_content_type="text/markdown",
    packages=['cfake'],
    package_data={'cfake': ['README.md', 'LICENSE']},
    install_requires=[],
    entry_points={
        'console_scripts': [
            'cfake = cfake.fake:run'
        ]
    }
)
