
import subprocess
output = subprocess.getoutput("ls -l")
print(output)

from argparse import ArgumentParser
from sharpai_api import SharpAIFolder,SA_API

from commands import BaseSharpAICLICommand
from utils.get_id import get_id

class BaseDeepCameraCommands(BaseSharpAICLICommand):
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
            "start", help="stop deepcamera"
        )

        deepcamera_start_parser.set_defaults(func=lambda args: DeepCameraStartCommand(args))
        deepcamera_stop_parser.set_defaults(func=lambda args: DeepCameraStopCommand(args))
class BaseDeepCameraCommands:
    def __init__(self, args):
        self.args = args
        self._api = SA_API()

class DeepCameraStartCommand(BaseDeepCameraCommands):
    def run(self):
        device_id = get_id().replace(':','')
        SharpAIFolder.save_device_id(device_id)

        self._api.register_device(device_id)
class DeepCameraStopCommand(BaseDeepCameraCommands):
    def run(self):
        device_id = None
        device_id = SharpAIFolder.get_device_id()

        if device_id is None:
            device_id = get_id().replace(':','')

        self._api.unregister_device(device_id)

