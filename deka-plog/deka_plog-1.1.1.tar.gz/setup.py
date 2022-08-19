from setuptools import setup, find_packages
setup(
    name='deka_plog',
    version='1.1.1',
    description='Output logs to console and files',
    author='zy',
    author_email='517826265@qq.com',
    install_requires=['concurrent_log_handler'],
    packages=find_packages(),
    py_modules=['deka_plog.filelock', 'deka_plog.handlers', 'deka_plog.log_manager', 'deka_plog.monkey_patch']
)