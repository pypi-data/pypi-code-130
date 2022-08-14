from setuptools import setup


setup(name='eme',
      version='5.2.3',
      description='Multi-purpose web framework',
      url='https://github.com/oboforty/eme',
      author='oboforty',
      author_email='rajmund.csombordi@hotmail.com',
      license='MIT',
      zip_safe=False,
      packages=[
          'eme',
          'eme/plugins',
          'eme/plugins/doors_oauth',
          'eme/plugins/doors_oauth/controllers',
          'eme/plugins/doors_oauth/dal',
          'eme/plugins/doors_oauth/groups',
          'eme/plugins/doors_oauth/services',
          'eme/_tools',
          'eme/_tools/commands'
      ],
      package_data={
          'eme/plugins/doors_oauth': ['templates/doors/*html'],
          'eme/_tools': ['content/*.tpl', 'modules/*.zip']
      },
      entry_points={
          'console_scripts': [
              'eme = eme._tools.cli:main',
          ],
      },
      install_requires=[
          'flask',
          'flask-login',
          'flask-mail',
          'websockets',
          'bcrypt',
          'inflect',
          'sqlalchemy',

          'authlib',
          'redis',
          'faker',
          'pynliner',
          'beautifulsoup4'
      ])
