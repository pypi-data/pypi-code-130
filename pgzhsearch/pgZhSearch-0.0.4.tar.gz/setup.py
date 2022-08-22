import setuptools
from pgZhSearch import version
from m2r import parse_from_file


# with open("README.md", "r", encoding='utf-8') as fh:
#     long_description = fh.read()
long_description = parse_from_file('pypi.md')     # .markdown必须转换为.rst, 否则有可能报错

setuptools.setup(
    name="pgZhSearch",
    version=version(),
    author="bode135",
    author_email='2248270222@qq.com',   # 作者邮箱
    description="django-postgresql-zh-full-text-search",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitee.com/bode135/pgZhSearch', # 主页链接
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['psycopg2-binary==2.9.1', 'jieba'],     # 依赖模块
    include_package_data=True,
)
