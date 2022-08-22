class Spoon(object):
    """Main spoon class"""

    def __init__(self):
        super(Spoon, self).__init__()

    def talk(self, message='¡Hola extraño!'):
        print(message)

    def spoon(self):
        print("Spoon")


spoon = Spoon()
spoon.talk(message='¡Hola amigo!')
