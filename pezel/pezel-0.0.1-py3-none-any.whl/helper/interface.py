import logging
import networkx as nx

from helper.logging import user_log_root


class BuildUI(object):
    SPACE_CHAR = ' '
    PREV_NODE_CHAR = '↑'
    CONNECT_NODE_CHAR = '↱'

    def __init__(self, root, graph):
        self.root = root
        self.graph = graph
        self.prev_drawing = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.prev_drawing = None

    def building_node(self, node):
        node_depth = nx.shortest_path_length(self.graph, self.root, node)

        connect = self.CONNECT_NODE_CHAR
        if node_depth == 0:
            connect = ' '

        if self.prev_drawing is None:
            drawing = self.SPACE_CHAR * node_depth
        elif len(self.prev_drawing) < node_depth:
            drawing = self.prev_drawing + self.PREV_NODE_CHAR + self.SPACE_CHAR * (node_depth - len(self.prev_drawing))
        else:
            drawing = self.prev_drawing[:node_depth]

        node_data = self.graph.nodes[node]['data']
        if not node_data.is_anonymous:
            user_log_root.info(f'{drawing}{connect}{node_data.str()}')
            self.prev_drawing = drawing
        elif user_log_root.level <= logging.DEBUG:
            user_log_root.debug(f'{drawing}{connect}{node_data.str()}')
            self.prev_drawing = drawing
