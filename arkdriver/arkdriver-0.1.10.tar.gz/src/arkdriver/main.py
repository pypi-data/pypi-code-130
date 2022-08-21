from arkclient import GameBotClient
from arklibrary.lib import Ini
from arkdriver import Admin
from pathlib import Path
from time import sleep

__testing__ = False


def run(interval=10):
    user_config = Path().cwd() / Path('config.ini')
    default_config = Path(__file__).parent / Path('config.ini')
    config = Ini(user_config) if user_config.exists() else Ini(default_config)
    password = config['ADMIN']['password']
    admin = Admin(password=password)
    admin.enable_admin()
    admin.execute()

    if not __testing__:
        with GameBotClient(server_id=123) as bot:
            while bot.connected:
                data = bot.ping()
                if data:
                    if isinstance(data, list):
                        admin.command_list += data
                        admin.execute()
                    sleep(interval)


if __name__ == "__main__":
    run()
