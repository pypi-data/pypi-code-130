import os


def setup_django_project(directory: str = '.'):
    os.chdir(directory)

    name = input('NAME - ')
    os.system('pip install django')
    print('django installed')
    os.system(f'django-admin startproject {name} {directory}')
    print('\033[92mDONE!\033[0m')
