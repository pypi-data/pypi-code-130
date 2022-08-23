from distutils.core import setup
# python setup.py sdist
# python -m twine upload --repository pypi dist/AztBacktrader-0.0.0.tar.gz
# pip install --upgrade AztBacktrader
import setuptools

setup(
    name='AztBacktrader',
    packages=setuptools.find_packages(),
    version='0.0.0',
    license='GNU Lesser General Public License v3.0',
    description='Wrapper From AztQuant Virtual Exchange Python Client To BackTrader',
    author='Qujamlee',
    author_email='qujamlee@126.com',
    url='https://gitee.com/Qujamlee/azt-backtrader',
    download_url='https://gitee.com/Qujamlee/azt-backtrader',
    keywords=['azt', 'aztve', 'backtrader', 'bt'],
    install_requires=[
        'backtrader',
        'AztVeClient',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # "3 - Alpha", "4 - Beta", "5 - Production/Stable"
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
