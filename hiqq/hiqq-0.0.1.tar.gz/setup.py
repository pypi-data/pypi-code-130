from setuptools import setup, find_packages

setup(
    name='hiqq',
    version='0.0.1',
    keywords='get_friend_list Robot get_group_chat information',
    description='a library for weixin robot',
    license='MIT License',
    url='',
    author='pythonnic',
    author_email='2696047693@qq.com',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=["requests"],
)
