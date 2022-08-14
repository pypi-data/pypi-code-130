import lichess.api
from lichess.format import PYCHESS

game = lichess.api.game('Qa7FJNk2', format=PYCHESS)
print(game.end().board())