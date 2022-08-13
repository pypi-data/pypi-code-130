import setuptools

setuptools.setup(
    name = 'async_get_vedio',
    version = '1.3',
    author = 'WUT_ljs',
    author_email = '3480339804@qq.com',
    url = 'https://github.com/wutljs/async_get_vedio',
    description = 'Get vedio',
    long_description = '此次更新,将async_get_vedio自动调用方法下载一个视频改为:async_get_vedio可以用于用户自定义的函数中被多次调用.'
                       '具体文档请进入:https://github.com/wutljs/async_get_vedio 查看.',
    packages = setuptools.find_packages(),
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ]
)