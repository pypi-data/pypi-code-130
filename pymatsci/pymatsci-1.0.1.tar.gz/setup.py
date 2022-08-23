from setuptools import setup, find_packages


def readme():
      f = open('README.rst')
      data = f.read()
      f.close()
      return data


setup(name="pymatsci", version='1.0.1', description='Python Materials Science', packages=find_packages(), author='C.L. Qin',
      author_email='clqin@foxmail.com', long_description=readme(), 
      url='https://pymatsci.readthedocs.io/en/latest/',
      license='MIT License (MIT)', install_requires=['numpy', 'pymatgen'], python_requires='>=3')