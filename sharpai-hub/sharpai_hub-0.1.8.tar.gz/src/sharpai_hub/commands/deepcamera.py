import os
import subprocess
import requests
from argparse import ArgumentParser
from shutil import which
from os.path import expanduser
import platform

from . import BaseSharpAICLICommand
from ..sharpai_api import SharpAIFolder,SA_API

class DeepCameraCommands(BaseSharpAICLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        deepcamera_parser = parser.add_parser(
            "deepcamera", help="{start,stop} deepcamera app control"
        )
        deepcamera_subparsers = deepcamera_parser.add_subparsers(
            help="device management command"
        )
        deepcamera_start_parser = deepcamera_subparsers.add_parser(
            "start", help="start deepcamera"
        )
        deepcamera_stop_parser = deepcamera_subparsers.add_parser(
            "stop", help="stop deepcamera"
        )

        deepcamera_start_parser.set_defaults(func=lambda args: DeepCameraStartCommand(args))
        deepcamera_stop_parser.set_defaults(func=lambda args: DeepCameraStopCommand(args))
class BaseDeepCameraCommands:
    def __init__(self, args):
        self.runtime_folder = expanduser("~/.sharpai/deepcamera")
        self.args = args
        self._api = SA_API()

    def check_credential(self):
        self.userInfo = SharpAIFolder.get_token()
        if self.userInfo is None:
            print('Please login with command: sharpai_cli login')
            exit(-1)
        device_id = SharpAIFolder.get_device_id()
        if device_id is None:
            print('Please register device with command: sharpai_cli device register')
            exit(-1)

    def check_environment(self):
        self.check_if_docker_installed()
        self.check_if_docker_has_permission()
        self.check_if_docker_compose_installed()

    def check_if_docker_installed(self):
        if which('docker'):
            pass
        else:
            print('docker is not installed, please install docker: https://docs.docker.com/engine/install/')
            exit(-1)
    def check_if_docker_compose_installed(self):
        if which('docker-compose'):
            self.docker_compose_path = which('docker-compose')
        else:
            print('docker-compose is not installed, please install docker-compose: pip install docker-compose')
            exit(-1)
    def check_if_docker_has_permission(self):
        output = subprocess.getoutput("docker ps")
        if 'CONTAINER ' not in output:
            print('Docker has no permission, please use following command to assign permission:\n')
            print('1. sudo groupadd docker\n')
            print('2. sudo userMod -aG docker $USER\n')
            print('3. newgrp docker\n')
            print('logout/login your account, if there\'s issue still, please reboot\n')
            #print(output)
            exit(-1)

class DeepCameraStartCommand(BaseDeepCameraCommands):
    def run(self):
        self.check_environment()
        self.check_credential()

        os.makedirs(self.runtime_folder, exist_ok=True)
        
        processor = platform.processor()
        print(processor)
        arch = None
        if processor == 'x86_64':
            arch = 'x86'
            docker_compose_yml = 'docker-compose-x86.yml'
        elif processor == 'i386':
            arch = 'x86'
            docker_compose_yml = 'docker-compose-x86.yml'
            
        if arch == None:
            print('Your platform is not supported, please file an issue on github for feature request: https://github.com/SharpAI/DeepCamera/issues')
            exit(-1)
        yml_url = f'https://raw.githubusercontent.com/SharpAI/applications/main/deepcamera/{docker_compose_yml}'
        env_url = 'https://raw.githubusercontent.com/SharpAI/applications/main/deepcamera/.env'
        
        yml_path = os.path.join(self.runtime_folder,'docker-compose.yml')
        env_path = os.path.join(self.runtime_folder,'.env')
        
        response=requests.get(yml_url)
        open(yml_path, "wb").write(response.content)

        response=requests.get(env_url)
        open(env_path, "wb").write(response.content)

        print('Downloaded the latest docker-compose.yml\n')
        print('Start to pull latest docker images, it will take a while for the first time\n')
        command = f'{self.docker_compose_path} -f {yml_path} pull'

        output = subprocess.getoutput(command)
        
        print('Starting DeepCamera with docker-compose\n')
        args = [self.docker_compose_path, '-f' , yml_path,'up']
        subprocess.Popen( args= args, cwd=self.runtime_folder)
        
class DeepCameraStopCommand(BaseDeepCameraCommands):
    def run(self):
        self.check_environment()
        
        yml_path = os.path.join(self.runtime_folder,'docker-compose.yml')
        
        args = [self.docker_compose_path, '-f' , yml_path,'down']
        subprocess.Popen( args= args, cwd=self.runtime_folder)

