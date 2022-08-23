class Hacker(object):
    """This will help you to hack anything!"""

    def __init__(self, hacker_name, target):
        super(Hacker, self).__init__()
        self.hacker_name = hacker_name
        self.target = target

    def lets_hack(self):
        print(self.hacker_name, " is the ", self.target, " hacker")

    def scape():
        print("Abort hacking and stay safe")


h = Hacker('Jalkhov', 'Pentagon')
h.lets_hack()
