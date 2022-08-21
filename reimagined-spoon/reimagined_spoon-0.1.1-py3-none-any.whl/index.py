class Spoon(object):
    """docstring for Spoon"""

    def __init__(self):
        super(Spoon, self).__init__()

    def talk(self, message='¡Hola extraño!'):
        print(message)

    def bug(self):
        if 1 > 2:
            print("1 es mayor que 2")
        elif 2 > 1:
            print("2 es mayor que 1")

    def spoon(self):
        print("Spoon")


spoon = Spoon()
spoon.talk(message='¡Hola amigo!')
