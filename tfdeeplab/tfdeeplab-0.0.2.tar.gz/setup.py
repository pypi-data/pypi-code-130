import setuptools

setuptools.setup(
    name='tfdeeplab',
    version='0.0.2',
    author='Reza Mohebbian',
    author_email='',
    description='Deeplab',
    long_description_content_type='text/markdown',

    packages=setuptools.find_packages(),
    license='Apache License 2.0',
    install_requires=["tensorflow-gpu==1.15"],
    python_requires='>=3.7, <3.8',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
    ]
)
