import json
import os
import jmespath
import sys


class TailScaleDeviceIp:

    @staticmethod
    def log(message: str):
        print('[tailscale-util-ns] ' + message)

    @staticmethod
    def value_at_json_path(json, path: str):
        expression = jmespath.compile(path)
        return expression.search(json)

    @staticmethod
    def tailscale_path():
        if sys.platform == 'darwin':
            path = os.getenv('TAILSCALE_PATH', default='/Applications/Tailscale.app/Contents/MacOS/Tailscale')
            if os.path.exists(path):
                return path
            else:
                raise RuntimeError('Please set `TAILSCALE_PATH` in environment variable. \n '
                                   'Example: export TAILSCALE_PATH=/Applications/Tailscale.app/Contents/MacOS/Tailscale')
        else:
            return 'tailscale'

    @staticmethod
    def is_stopped():
        results = TailScaleDeviceIp.get_status_details()
        jpath = "BackendState"
        status = TailScaleDeviceIp.value_at_json_path(results, jpath)
        value = True if str(status).lower() == 'stopped' else False
        TailScaleDeviceIp.log('Tailscale State is ' + status)
        return value

    @staticmethod
    def needs_login():
        results = TailScaleDeviceIp.get_status_details()
        jpath = "BackendState"
        status = TailScaleDeviceIp.value_at_json_path(results, jpath)
        value = True if str(status).lower() == 'needslogin' else False
        TailScaleDeviceIp.log('Tailscale State is ' + status)
        return value

    @staticmethod
    def auth_url():
        auth_url = None
        results = TailScaleDeviceIp.get_status_details()
        jpath = "BackendState"
        status = TailScaleDeviceIp.value_at_json_path(results, jpath)
        value = True if str(status).lower() == 'needslogin' else False
        if value:
            jpath = "AuthURL"
            auth_url = TailScaleDeviceIp.value_at_json_path(results, jpath)
            TailScaleDeviceIp.log('Tailscale Auth URL is ' + auth_url)
        else:
            TailScaleDeviceIp.log('Tailscale is already logged in with user')
        return auth_url

    @staticmethod
    def up():
        command = f"{TailScaleDeviceIp.tailscale_path()} up"
        TailScaleDeviceIp.log('Executing command: ' + command)
        os.popen(command).read()

    @staticmethod
    def down():
        command = f"{TailScaleDeviceIp.tailscale_path()} down"
        TailScaleDeviceIp.log('Executing command: ' + command)
        os.popen(command).read()

    @staticmethod
    def get_status_details():
        command = f"{TailScaleDeviceIp.tailscale_path()} status --json"
        TailScaleDeviceIp.log('Executing command: ' + command)
        output = os.popen(command).read()
        return json.loads(output)

    @staticmethod
    def get_ip_for_all_devices():
        results = TailScaleDeviceIp.get_status_details()
        jpath = "Peer.*.{device: HostName,ip: TailscaleIPs[0]}]"
        return TailScaleDeviceIp.value_at_json_path(results, jpath)

    @staticmethod
    def get_ip_for_device(device_name: str):
        results = TailScaleDeviceIp.get_status_details()
        jpath = "Peer.{device:*}.device[?HostName==`" + device_name + "`].TailscaleIPs | [0] | [0]"
        value = TailScaleDeviceIp.value_at_json_path(results, jpath)
        TailScaleDeviceIp.log('IP Address for device `' + device_name + '` is ' + value)
        return value

    @staticmethod
    def prepare():
        if TailScaleDeviceIp.is_stopped():
            TailScaleDeviceIp.up()
            TailScaleDeviceIp.is_stopped()
