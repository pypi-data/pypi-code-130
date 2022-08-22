from .libs import *
class obj:
    def __init__(self):
        pass
    def render(self, x, y):
        pass
    def abs_(self, i, j):
        return abs(complex(i, j))
def render(obj_, width, heigth):
    p = []
    for i in range(width):
        p.append([])
        for j in range(heigth):
            r = obj_.render(i - width / 2, j - heigth / 2)
            if r < 1:
                p[len(p)-1].append((255, 255, 255))
            else:
                p[len(p)-1].append((0, 0, 0))
    return np.array(p)