from setuptools import setup

setup(name='multi-exe-maker',
    version='0.3',
    long_description=''.join(open('README.md', encoding='utf-8').readlines()),
    long_description_content_type='text/markdown',
    author="Vitor Augusto de Lima Soares",
    author_email="vitoraugustodelimasoares@gmail.com",
    description='This program can make a lot of executables files at the same time, in order to save time',
    packages=['multi_exe_maker'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'multi_exe_maker=multi_exe_maker.multi_exe_maker:run'
        ],
    })