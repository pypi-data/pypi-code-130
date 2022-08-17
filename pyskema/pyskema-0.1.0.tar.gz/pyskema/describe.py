from .schema import Node, Atom, AtomType, Record, Tuple
from .visitor import Visitor
from .misc import closest, lev_dist


def describe(schema, selects=()):
    res = select(schema, selects)

    if not res:
        i = res.err

        if i == 0:
            raise KeyError(f"There is no {selects[0]} field in this schema.")
        else:
            raise KeyError(
                f"There is no {selects[i]} field in " + ".".join(selects[:i]) + "."
            )

    if selects != ():
        print(".".join(selects) + ":")

    for s in Describer.describe(res.val):
        print(s)


def select(schema, selects, index=0):
    if selects in {("all",), ("",)}:
        return Result.ok(schema)

    if index < len(selects) - 1:
        if (
            isinstance(schema.structure, (Record, Tuple))
            and selects[index] in schema.structure.fields
        ):
            node = schema.structure.fields[selects[index]]
            return select(node, selects, index=index + 1)
        else:
            return Result.error(index)
    else:
        return Result.ok(schema.structure.fields[selects[index]])


class Describer(Visitor):
    @classmethod
    def describe(cls, schema):
        """Show the visit"""
        yield from cls().describe_node(schema)

    def visit_atom(self, atom, indent=0):
        indent_str = "  " * indent
        message = [f"{indent_str}"]

        if atom.type_ == AtomType.BOOL:
            message.append("bool")

        elif atom.type_ == AtomType.INT:
            message.append("int")

        elif atom.type_ == AtomType.STR:
            message.append("str")

        elif atom.type_ == AtomType.OPTION:
            if len(atom.options) == 1:
                message.append(repr(atom.options[0]))
            else:
                message.append("one of ")
                message.append(", ".join(map(repr, atom.options[:-1])))
                message.append(f", or {repr(atom.options[-1])}")

        elif atom.type_ == AtomType.FLOAT:
            message.append("float")

        else:
            raise NotImplementedError(f"{atom.type_} is not implemented in Describer.visit_atom.")

        yield "".join(message)

    def visit_union(self, union, indent=0):
        indent_str = "  " * indent

        if len(union.options) > 1:
            yield indent_str + "one of the following options:"
            pfx = indent_str + "- "
            ind = indent + 1
        else:
            pfx = ""
            ind = indent
        for i, op in enumerate(union.options):
            yield from self.describe_node(op, prefix=pfx, indent=ind)

    def visit_record(self, rec, indent=0):
        indent_str = "  " * indent
        for key, node in rec.fields.items():
            yield from self.describe_node(
                node, prefix=f"{indent_str}{key}: ", indent=indent + 1,
            )

    def visit_tuple(self, tup, indent=0):
        indent_str = "  " * indent
        for value in tup:
            yield from self.describe_node(
                value, prefix=f"{indent_str}- ", indent=indent + 1,
            )

    def visit_collection(self, collection, indent=0):
        indent_str = "  " * indent
        yield f"{indent_str}a list of{indent_str}"
        yield from self.visit(collection.element, indent=indent + 1)

    def visit_map(self, map, indent=0):
        yield from self.visit(
            map.element, indent=indent + 1
        )

    def describe_node(self, value, prefix="", indent=0):
        indent_str = "  " * indent
        message = [prefix]

        if value.description:
            message.append(value.description)

        if value.optional:
            message.append(
                f"\n{indent_str} (optional, default is {repr(value.default)})"
            )

        msg = "".join(message)

        if msg:
            yield msg

        yield from self.visit(value, indent=indent + 1)


class Result:
    def __init__(self, valid, val, err):
        self.val = val
        self.err = err
        self.valid = valid

    @classmethod
    def error(cls, err):
        return cls(False, None, err)

    @classmethod
    def ok(cls, val):
        return cls(True, val, None)

    def __bool__(self):
        return self.valid


def search(schema, name):
    likely = sorted(Searcher.search(schema, name))
    return [".".join(p) for _, p in likely]


class Searcher(Visitor):
    @classmethod
    def search(cls, schema, name):
        """Show the visit"""
        yield from cls().visit(schema, name)

    def visit_atom(self, atom, name, path=()):
        return ()

    def visit_union(self, union, name, path=()):
        for op in union.options:
            yield from self.visit(op, name, path)

    def visit_record(self, rec, name, path=()):
        for key, node in rec.fields.items():
            yield (lev_dist(key, name), (*path, key))
            yield from self.visit(node, name, (*path, key))

    def visit_tuple(self, tup, name, path=()):
        for i, value in enumerate(tup.fields):
            yield from self.visit(
                value,
                name,
                (*path, i),
            )

    def visit_collection(self, collection, name, path=()):
        yield from self.visit(collection.element, name, path)

    def visit_map(self, map, name, path=()):
        yield from self.visit(map.element, name, path)
