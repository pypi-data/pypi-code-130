import setuptools

with open('README.md','r',encoding='utf-8') as fh:
    description = fh.read()

setuptools.setup(
    name='paddleiv',
    version = '0.0.0.7',
    author = 'Xuheng Cao',
    author_email = 'caoxuhengcn@gmail.com',
    description = '适用于 Paddle2.0+ 的图像处理库',
    long_description = 'PaddleIv 基于Imgvision0.1.7+ 包括新的图像处理方案。如果卷积网络参数初始化、适用于图像的损失函数、图像退化卷积等',
    url = 'https://github.com/Caoxuheng',
    classifiers = ['License :: OSI Approved :: MIT License',
                   ],
    package_data = {

            '': ['*.npy'],
            # # 包含demo包data文件夹中的 *.dat文件
            # 'demo': ['data/*.dat'],
        },
    inculde_package_data = True,
    install_requires = ['numpy','imgvision'],
    packages =setuptools.find_packages(),
)