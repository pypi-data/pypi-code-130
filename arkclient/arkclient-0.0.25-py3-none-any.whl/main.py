from arkclient import GameBotClient, APIClient
from time import sleep


def test():
    with GameBotClient(server_id=123) as bot:
        for i in range(3):
            response = bot.ping()
            sleep(1)

    with APIClient() as bot:
        data = {"server_id": 123, "commands": ["cheat admin"]}
        response = bot.commands(data)

    with GameBotClient(server_id=123) as bot:
        for i in range(3):
            response = bot.ping()
            sleep(1)


if __name__ == "__main__":
    test()


