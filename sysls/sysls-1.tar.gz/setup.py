from setuptools import setup

setup(name='sysls',
      version='1',
      description='Display /sysfs values in a nice way',
      url='https://git.sr.ht/~martijnbraam/sysls',
      author='Martijn Braam',
      author_email='martijn@brixit.nl',
      packages=['sysls'],
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      ],
      entry_points={
          'console_scripts': ['sysls=sysls.__main__:main'],
      })
