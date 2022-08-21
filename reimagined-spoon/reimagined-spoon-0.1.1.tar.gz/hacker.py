class Hacker(object):
    """This will help you to hack the NASA
    and of course, with educational purposes only :)"""

    def __init__(self, hacker_name):
        super(Hacker, self).__init__()
        self.hacker_name = hacker_name

    def lets_hack(self):
        print(self.hacker_name, "cant hack NASA yet :(")


h = Hacker('Jalkhov')
h.lets_hack()
