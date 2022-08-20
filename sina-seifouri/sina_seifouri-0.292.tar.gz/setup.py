from setuptools import setup, find_packages


setup(
    name='sina_seifouri',
    version='0.292',
    license='MIT',
    author="Sina Seifouri",
    author_email='sinasox@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/sinasox/sina_seifouri',
    keywords='This is just an introduction.',
    entry_points={
        'console_scripts': [
            'sina_seifouri=sina_seifouri:main'
        ]
    },
    install_requires=[
    'requests'

    ],

)
