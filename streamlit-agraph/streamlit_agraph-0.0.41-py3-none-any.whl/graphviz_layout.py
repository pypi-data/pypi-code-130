from streamlit_agraph.node import Node

def _set_graphviz_layout(nodes, edges, config):
    try:
        import pygraphviz as pgv
    except ImportError as e:
        raise ImportError("requires pygraphviz " "http://pygraphviz.github.io/") from e

    G = pgv.AGraph(**getattr(config, 'graphviz_config'))
    node_args = {}
    for node in nodes:
        node_id = getattr(node, 'id')
        G.add_node(node_id)
        node_args[node_id] = node.to_dict()
    for edge in edges:
        G.add_edge(getattr(edge, 'source'), getattr(edge, 'target'))
    G.layout(getattr(config, 'graphviz_layout'))

    for n in G.nodes():
        node = G.get_node(n)
        try:
            xs = node.attr["pos"].split(",")
            node_args[node.get_name()].update({'x': float(xs[0]),
                                               'y': float(xs[1])})
        except:
            print("no position for node", n)
            node_args[node.get_name()].update({'x': 0, 'y': 0})

    nodes = [Node(**node_args[n]) for n in G.nodes()]

    return nodes, edges