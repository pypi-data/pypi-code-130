from arkclient import GameBotClient
from arkdriver.lib import Ini
from arkdriver import Admin
from pathlib import Path
from time import sleep

__testing__ = False


def run():
    user_config = Path().cwd() / Path('config.ini')
    default_config = Path(__file__).parent / Path('config.ini')
    config = Ini(user_config) if user_config.exists() else Ini(default_config)
    password = config['ADMIN']['password']
    admin = Admin(password=password)
    admin.enable_admin()
    admin.execute()

    if not __testing__:
        with GameBotClient('bot') as bot:
            while True:
                response = bot.send("ping")
                data = response.decode()
                admin.command_list += data
                admin.execute()
                sleep(5)


if __name__ == "__main__":
    run()
