from setuptools import setup, find_packages

setup(
    name='Mensajes-LucasBoff',
    version='5.0',
    description='Un paquete para saludar y despedir',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Luqui',
    author_email='luqui@gmail.com',
    url='https://www.lqui.dev',
    license_files=['LICENSE'],
    packages=find_packages(),
    scripts=[],
    test_suite='tests',
    install_requires=[paquete.strip() for paquete in open('requirements.txt').readlines()],
    classifiers=['Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]

)