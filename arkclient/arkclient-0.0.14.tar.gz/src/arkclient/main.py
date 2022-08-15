from arkclient.client import GameBotClient
from time import sleep


def test():
    with GameBotClient("bot") as bot:
        for i in range(3):
            response = bot.send('ping')
            sleep(1)

    with GameBotClient("api") as bot:
        response = bot.send("cheat admin")

    with GameBotClient("bot") as bot:
        for i in range(3):
            response = bot.send('ping')
            sleep(1)


if __name__ == "__main__":
    test()


