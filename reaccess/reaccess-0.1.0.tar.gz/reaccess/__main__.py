import readline
import getpass

import argeasy

from . import server
from . import client
from .__init__ import __version__


def main():
    parser = argeasy.ArgEasy(
        project_name='REaccess',
        description='Execute commands on another machine remotely.',
        version=__version__
    )

    parser.add_argument('server', 'Start server', action='store_true')
    parser.add_argument('client', 'Start client', action='store_true')

    parser.add_flag('--host', 'Set the connection host')
    parser.add_flag('--port', 'Set the connection port')

    args = parser.get_args()

    if args.server:
        password = getpass.getpass('Add password to connection (empty for no password): ')

        if not password:
            password = None

        master = server.Server(args.host, args.port, password)
        master.run()

        print('Running server...')
    elif args.client:
        clientc = client.Client(args.host, args.port)

        if clientc.required_password():
            while True:
                password = getpass.getpass('Enter the password: ')
                correct_pw = clientc.check_password(password)

                if not correct_pw:
                    print('\033[31mIncorrect password. Try again.\033[m')
                else:
                    break

            while True:
                cmd = input('reaccess (cmd) > ').strip()
                clientc.send_command(cmd)
