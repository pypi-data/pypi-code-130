#! /usr/bin/env python
# encoding: utf-8

import unittest


from confusion.utils.toml2dot import Model
from confusion.utils.toml2dot import Node


class TestLoad(unittest.TestCase):

    def test_tables(self):
        text = """
        [A]
        tag = 1

        [A.B.C]
        tag = 1

        [  D ]
        """
        model = Model.loads(text)
        self.assertEqual(["A", "A.B.C", "D"], list(model.tables.keys()))

    def test_table(self):
        text = """
        [A]
        tag = 1

        [A.B.C]
        tag = 2

        [  D ]
        """
        model = Model.loads(text)
        self.assertEqual(1, model.tables["A"].get("tag"))
        self.assertEqual({"tag": 2}, model.tables["A.B.C"])

    def test_get(self):
        text = """
        [A.B.C]
        tag = 1
        """
        model = Model.loads(text)
        self.assertEqual({"tag": 1}, model.tables["A.B.C"])

    def test_graphs_unique(self):
        text = """
        [A]
        graphs = ["a", "b"]
        [B]
        [C]
        graphs = ["a"]
        """
        model = Model.loads(text)
        self.assertEqual({"a", "b"}, model.graphs)
        for i in ("A", "B", "C"):
            with self.subTest(i=i):
                self.assertFalse(model.is_arc(model.data[i]))

    def test_graphs_sublevels(self):
        text = """
        [A]
        graphs = ["a"]
        [A.B]
        graphs = ["b"]
        """
        model = Model.loads(text)
        self.assertEqual({"a", "b"}, model.graphs)

    def test_loads(self):
        text = """
        [A]
        [B]
        """
        model = Model.loads(text)
        self.assertIsInstance(model, Model)

    def test_dumps(self):
        text = """
        [A]
        [B]
        """
        model = Model.loads(text)
        self.assertIsInstance(model, Model)


class TestNode(unittest.TestCase):

    def test_node_defaults(self):
        self.assertRaises(TypeError, Node)
        node = Node(name="test node")
        self.assertEqual("test node", node.label)
        self.assertEqual(1, node.weight)
        self.assertIsInstance(node.weight, float)
        self.assertEqual([], node.arcs)
        self.assertTrue(hash(node))

    def test_node_parent_root(self):
        text = """
        [A]
        [B]
        """
        model = Model.loads(text)
        self.assertEqual(2, len(model.nodes))
        self.assertEqual("A", model.nodes["A"].label)
        self.assertTrue(all(i.parent is None for i in model.nodes.values()))
        self.assertTrue(all(isinstance(i.data, dict) for i in model.nodes.values()))

    def test_node_parent_tree(self):
        text = """
        [A]
        [A.B]
        [C]
        [C.B]
        """
        model = Model.loads(text)
        self.assertEqual(4, len(model.nodes))
        self.assertEqual("A", model.nodes["A"].label)
        self.assertEqual("A", model.nodes["A.B"].parent)
        self.assertEqual("C", model.nodes["C.B"].parent)

    def test_node_parent_gap(self):
        text = """
        [A]
        [C.B.C]
        [C]
        [A.B.C]
        """
        model = Model.loads(text)
        self.assertEqual(4, len(model.nodes))
        self.assertEqual("A", model.nodes["A.B.C"].parent)
        self.assertEqual("C", model.nodes["C.B.C"].parent)

    def test_node_children(self):
        text = """
        [A]
        [C.B.C]
        [C]
        [A.B.C]
        """
        model = Model.loads(text)
        self.assertEqual(4, len(model.nodes))
        self.assertEqual(["A.B.C"], model.children("A"))
        self.assertEqual("C", model.nodes["C.B.C"].parent)

    def test_node_rank(self):
        text = """
        [A]
        [C.B.C]
        [C]
        [A.B.C]
        """
        model = Model.loads(text)
        self.assertEqual(0, model.nodes["A"].rank)
        self.assertEqual(2, model.nodes["A.B.C"].rank)
        print(model.children("A"))

    def test_arc_labels(self):
        text = """
        [A.B]
        [A.B.c]
        target = "C"
        [C]
        [C.ab]
        target = "A.B"
        """
        model = Model.loads(text)
        self.assertEqual(2, len(model.nodes))
        self.assertEqual(1, len(model.nodes["A.B"].arcs))
        self.assertEqual(1, len(model.nodes["C"].arcs))

    def test_node_to_dot(self):
        text = """
        [A]
        [C.B.C]
        [C]
        [A.B.C]
        """
        model = Model.loads(text)
        self.assertEqual(4, len(model.nodes))
        self.assertEqual("C", model.nodes["C.B.C"].parent)
