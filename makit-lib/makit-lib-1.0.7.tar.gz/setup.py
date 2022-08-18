from setuptools import setup

setup(
    name='makit-lib',
    version='1.0.7',
    packages=[
        'makit.lib',
        'makit.lib.collections',
        'makit.lib.logging'
    ],
    namespace_package=['makit'],
    install_requires=[
        'deprecated'
    ],
    python_requires='>3.3',
    url='https://gitee.com/liangchao0728/makit-lib',
    license='MIT',
    author='LiangChao',
    author_email='liang20201101@163.com',
    description='实用工具包，对python基础库的扩展'
)
