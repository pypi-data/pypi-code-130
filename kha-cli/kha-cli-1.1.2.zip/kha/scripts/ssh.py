import os
import json
import struct
import fcntl
import termios
import signal
import sys

import click
import pexpect
import inquirer
from inquirer.render.console import ConsoleRender
from inquirer.themes import Default

from kha.const import BASE_CONFIG_PATH
from kha.utils.file_utils import exists


class TerminalSizer:
    def __init__(self, process):
        self.process = process

    def get_size(self):
        """Return tuple with rows, columns"""
        s = struct.pack("HHHH", 0, 0, 0, 0)
        a = struct.unpack('hhhh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s))
        return a[0], a[1]

    def __enter__(self):
        self.process.setwinsize(*self.get_size())
        signal.signal(signal.SIGWINCH, self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.signal(signal.SIGWINCH, signal.SIG_DFL)

    def __call__(self, sig, data):
        if not self.process.closed:
            self.process.setwinsize(*self.get_size())


class MyTheme(Default):
    def __init__(self):
        super().__init__()


@click.command()
@click.pass_context
def ssh(ctx):
    config_filepath = os.path.join(BASE_CONFIG_PATH, 'ssh', 'default.json')
    if not exists(config_filepath):
        click.echo('🦄 嘿，没找到配置文件。')
        return
    try:
        with open(os.path.join(BASE_CONFIG_PATH, 'ssh', 'default.json')) as ssh_config:
            server_list = json.load(ssh_config)['server_list']
    except Exception as e:
        click.echo('🦄 嘿，配置文件错误。')
        return
    server_dict = {i['name']: i for i in server_list}
    if len(server_list) != len(server_dict):
        click.echo('🦄 嘿，服务器配置name重复。')
        return

    selected_server = inquirer.list_input(
        message="使用 ↓ ↑ 选择要登录的服务器",
        render=ConsoleRender(theme=MyTheme()),
        choices=[f"{s.get('name')} > {s.get('user')}@{s.get('host')}" for s in server_list])
    server = server_dict.get(selected_server.split(' > ')[0])

    if 'password' in server:
        cmd = f'ssh -p {server["port"]} {server["user"]}@{server["host"]}'
        child = pexpect.spawn(cmd)
        i = child.expect(['password:', 'continue connecting (yes/no)?'], timeout=5)
        if i == 0:
            child.sendline(server['password'])
        elif i == 1:
            child.sendline('yes\n')
            child.expect('password: ')
            child.sendline(server['password'])
    else:
        cmd = f'ssh -i {server["private_key"]} -p {server["port"]} {server["user"]}@{server["host"]}'
        child = pexpect.spawn(cmd)
        i = child.expect([pexpect.TIMEOUT, 'continue connecting (yes/no)?'], timeout=5)
        if i == 1:
            child.sendline('yes\n')

    index = child.expect(["#", pexpect.EOF, pexpect.TIMEOUT])
    if index == 0:
        with TerminalSizer(child):
            child.interact()
    elif index == 1:
        click.echo(f'🦄 {server["user"]} 用户登录失败')
    elif index == 2:
        click.echo(f'🦄 {server["user"]} 用户登录失败')
