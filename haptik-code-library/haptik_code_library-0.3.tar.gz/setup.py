from setuptools import setup

setup(name='haptik_code_library',
      version='0.3',
      description='components to handle chat flow',
      url='http://github.com/hellohaptik/',
      author='Haptik',
      author_email='eng@haptik.co',
      license='MIT',
      packages=[
          'haptik_code_library',
          'haptik_code_library.haptik_requests'
      ],
      install_requires=[
          "setuptools>=42",
          "wheel",
          "requests>=2.22.0,<=2.28.1"
      ],
      zip_safe=False)
