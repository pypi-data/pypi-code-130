from setuptools import find_packages, setup

setup(
    name='EMS_requests_handler_v1',
    packages=find_packages(include=['EMS_requests_helper']),
    version='0.0.2',
    license='EMS',
    description='Упрощенные команды для обращения к API в рамках тестирования EMS',
    author='Роман Перваков',
    install_requires=['requests']
)
