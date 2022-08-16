
class Find:
    def __init__(self, yt, caption, time):
        self.yt = yt
        self.caption = caption
        self.time = time

    def __str__(self):  # X
        return '<Find (yt_find=' + str(self.yt) + ')>'

    def __repr__(self):
        content = ' ;\n '.join([
            'yt=' + str(self.yt),
            'caption=' + str(self.caption),
            'time=' + str(self.time)
        ])
        return '\n<Find(' + content + ')>'


