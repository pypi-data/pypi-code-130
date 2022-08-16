from distutils.core import setup

setup(
    name='nonebot_plugin_PicMenu',
    packages=['nonebot_plugin_PicMenu'],
    version='0.2',
    license='MIT',
    description='A Plugin for Nonebot2 to generate picture menu of Plugins',
    author='hamo-reid',
    author_email='190395489@qq.com',
    url='https://github.com/hamo-reid/nonenot_plugin_PicMenu',
    install_requires=[
        'pillow',
        'fuzzywuzzy',
        'pydantic',
        'nonebot2',
        'nonebot-adapter-onebot'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ]
)