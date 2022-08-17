from arkclient import GameBotClient
from time import sleep


def test():
    with GameBotClient(type="bot") as bot:
        for i in range(3):
            response = bot.send('ping')
            sleep(1)

    with GameBotClient(type="api") as bot:
        response = bot.send("cheat admin")

    with GameBotClient(type="bot") as bot:
        for i in range(3):
            response = bot.send('ping')
            sleep(1)


if __name__ == "__main__":
    test()


