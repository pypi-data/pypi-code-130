from distutils.core import setup, Extension
setup(name = 'qconf_py', version = '1.2.2', ext_modules = [Extension('qconf_py', ['lib/python_qconf.cc'],
     include_dirs=['/home/rong/qconf/qconf/include'],
     extra_objects=['/home/rong/qconf/qconf/lib/libqconf.a']
     )])
