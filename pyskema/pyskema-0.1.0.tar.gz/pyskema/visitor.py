from .schema import Node


class Visitor:
    def visit(self, node: Node, *args, **kwargs):
        return node.structure.accept(self, *args, **kwargs)

    def visit_atom(self, atom, *args, **kwargs):
        pass

    def visit_union(self, union, *args, **kwargs):
        for node in union.options:
            self.visit(node, *args, **kwargs)

    def visit_record(self, rec, *args, **kwargs):
        for _, node in rec.fields.items():
            self.visit(node, *args, **kwargs)

    def visit_collection(self, collection, *args, **kwargs):
        self.visit(collection.element)

    def visit_map(self, map_, *args, **kwargs):
        self.visit(map_.element)

    def visit_tuple(self, tup, *args, **kwargs):
        for node in tup.fields:
            self.visit(node, *args, **kwargs)
