from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_desc = (this_directory / "README.md").read_text()

setup(
    name='pytest_ver',
    include_package_data=True,
    packages=find_packages(include='pytest_ver*', ),
    version='0.0.6',
    license='MIT',
    description='Pytest module with Verification Report',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    author='JA',
    author_email='cppgent0@gmail.com',
    url='https://github.com/cppgent0/pytest-ver',
    download_url='https://github.com/cppgent0/pytest-ver/archive/refs/tags/v_0_0_4.tar.gz',
    keywords=['verification', 'pytest'],
    install_requires=[
        'reportlab',
        'pytest',
        'jsmin',
    ],
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing :: Acceptance',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
)
