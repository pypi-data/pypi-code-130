from distutils.core import setup
from setuptools import find_packages
import os, sys
path = os.path.dirname('/'.join(os.path.abspath(__file__).split('/')[:-1]))
sys.path.append(path)


try:
    with open('/Users/ymdt/src/dreem_herschlag/requirements.txt') as f:
        requirements = f.read().splitlines()
except:
    with open('../requirements.txt') as f:
        requirements = f.read().splitlines()

PYTHON_VERSION = (3,10)

if sys.version_info < PYTHON_VERSION:
    sys.exit(f"Python >= {PYTHON_VERSION[0]}.{PYTHON_VERSION[1]} required.")


setup(
   name='dreem_herschlag',
   version= '1.1.4',
   license="MIT",
   description='A wrapper for DREEM for the Herschlag lab',
   author='Yves Martin des Taillades',
   author_email='yves@martin.yt',
   long_description= 'TODO',
 #  packages=['dreem_herschlag'],  #same as name
   package_dir={'dreem_herschlag': 'dreem_herschlag'},
   packages=find_packages(),
   package_data={'': ['*.yml']},
   py_modules=[
         'dreem_herschlag/sanity_check',
         'dreem_herschlag/run_dreem',
         'dreem_herschlag/run',
         'dreem_herschlag/util',
         'dreem_herschlag/template',
         'dreem_herschlag/get_info',
   ],
   include_package_data=True,
   install_requires=requirements, #external packages as dependencies
    entry_points = {
        'console_scripts' : [
            'dreem_herschlag = dreem_herschlag.run : main'
            ]
    },
    url='https://github.com/yvesmartindestaillades/dreem_herschlag'
)