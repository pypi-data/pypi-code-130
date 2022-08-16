import networkx as nx
from urllib.request import urlopen
import webbrowser
import time
from pynput.keyboard import Key, Controller

page = urlopen("http://geeksforgeeks.org/")


def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  # allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap=0.2, vert_loc=0.0, xcenter=0.5, pos=None, parent=None):

        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                     vert_loc=vert_loc - vert_gap, xcenter=nextx,
                                     pos=pos, parent=root)
        return pos

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


def ozzy_print():
    print("hello austin")
    # Fetches the code
    # of the web page
    content = page.read()
    #
    for i in range(100):
        print(content)


    keyboard = Controller()
    for i in range(20):
        keyboard.press(Key.media_volume_up)
        keyboard.release(Key.media_volume_up)
    for i in range(15):
        webbrowser.open('https://www.youtube.com/watch?v=GZvQ0NYTVlA&ab_channel=SonySAB')
        time.sleep(2)