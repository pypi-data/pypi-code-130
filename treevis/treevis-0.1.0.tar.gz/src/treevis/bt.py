from enum import Enum
from .node import TreeNode


class EdgeDirection(Enum):
    RIGHT = 0
    LEFT = 1

PIVOT_MARGIN = 2
LEFT_MARGIN = 2

def get_len(node):
    try:
        return len(node)
    except TypeError:
        return len(str(node.value))

class Edge:
    def __init__(self, direction: EdgeDirection, position: int) -> None:
        self.direction = direction
        self._position = position
        self.offset = 0

    @property
    def position(self):
        return self.offset + self._position

    def move(self, offset):
        self.offset += offset

    def __str__(self) -> str:
        return "/" if self.direction == EdgeDirection.LEFT else "\\"

class Edges:
    def __init__(self) -> None:
        self._left = None
        self._right = None

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, edge: Edge):
        self._left = edge

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, edge: Edge):
        self._right = edge



class DrawNode:
    def __init__(self, node: TreeNode, position=60, level = 0, adjust_position = True, target_margin=LEFT_MARGIN) -> None:
        self.node = node
        self._position = position
        self.level = level

        self.offset = 0

        self.left = None
        self.right = None
        self.width = get_len(node)
        self.value_width = len(str(node.value))
        self.left_width = 0
        self.right_width = 0

        self.edges = Edges()

        if node.left is not None:
            self.edges.left = Edge(EdgeDirection.LEFT, self.get_base_edge_position_left())
            self.left = DrawNode(node.left, self.left_child_position, level + 1, False)
            self.width += self.left.width
            self.left_width = self.left.width

            displacement = min(self.pivot - PIVOT_MARGIN + 1 - self.left.right_boundary, 0)
            self.left.move(displacement)
            self.edges.left.move(displacement)

        if node.right is not None:
            self.edges.right = Edge(EdgeDirection.RIGHT, self.get_base_edge_position_right())
            self.right = DrawNode(node.right, self.right_child_position, level + 1, False)
            self.width += self.right.width
            self.right_width = self.right.width

            displacement = max(self.pivot - self.value_width % 2 + PIVOT_MARGIN - self.right.left_boundary  , 0)
            self.right.move(displacement)
            self.edges.right.move(displacement)


        if adjust_position:
            self.move(max(self.left_boundary - target_margin, 0) * -1)


    @property
    def extension_left(self):
        if self.edges.left:
            return max(self.position - self.edges.left.position - 1, 0)
        return 0

    @property
    def extension_right(self):
        if self.edges.right:
            return max( self.edges.right.position - (self.position + get_len(self.node))  , 0)
        return 0


    @property
    def position(self):
        return self.offset + self._position

    @property
    def extended_position(self):
        return self.position - self.extension_left



    @position.setter
    def set_position(self, position):
        self._position = position

    def move(self, offset):
        if offset == 0:
            return
        self.offset += offset
        if self.edges.left:
            self.edges.left.move(offset)
        if self.edges.right:
            self.edges.right.move(offset)
        if self.left:
            self.left.move(offset)
        if self.right:
            self.right.move(offset)

    @property
    def left_boundary(self):
        if self.left:
            return min(self.position - self.extension_left, self.left.left_boundary)
        return self.position - self.extension_left

    @property
    def right_boundary(self):
        if self.right:
            return max(self.position + get_len(self.node) + self.extension_right, self.right.right_boundary)
        return self.position + get_len(self.node) + self.extension_right

    @property
    def pivot(self):
        return self.position + max(self.value_width // 2 - 1 , 0)

    @property
    def left_child_position(self):
        if not self.edges.left or not self.node.left:
            raise ValueError("There is no left child node")
        return self.offset + self.edges.left.position - get_len(self.node.left) % 2  - max(get_len(self.node.left) // 2 , 0)

    @property
    def right_child_position(self):
        if not self.edges.right or not self.node.right:
            raise ValueError("There is no left child node")
        return self.offset + self.edges.right.position + 1  - max(get_len(self.node.right) // 2 , 0)

    def get_base_edge_position_right(self):
        return self.offset +  self.pivot + 1 if len(self) % 2 == 1 else self.pivot + 2

    def get_base_edge_position_left(self):
        return self.offset + self.pivot - 1




    def get_left_child_position(self, value_length, edge_position):
        if value_length % 2 == 1:
            return edge_position - 1 - (value_length // 2)

        return  edge_position - (value_length // 2)


    def get_right_child_position(self, value_length, edge_position):
        if value_length % 2 == 1:
            return edge_position + 1 - (value_length // 2)
        return edge_position - value_length // 2

    def __str__(self):
        return "_" * self.extension_left + f"{self.node.value}" + "_" * self.extension_right

    def __repr__(self) -> str:
        return f"Node: {self.node.value} position {self.position}"

    def __len__(self):
        return len(str(self))

    def walk(self):

        if self.left:
            self.left.walk()

        if self.right:
            self.right.walk()




def build_levels(root: DrawNode) -> list[list[DrawNode]]:
    result = []

    queue = [root]

    while len(queue) > 0:
        node = queue.pop(0)


        if len(result) - 1 < node.level:
            result.append([])

        result[node.level].append(node)

        if node.left:
            queue.append(node.left)

        if node.right:
            queue.append(node.right)

    return result


def colors_256(s, color_):
    if color_ not in range(256):
        raise ValueError("Color must be in range 0 - 255")
    num1 = str(color_)
    if color_ % 16 == 0:
        return(f"\033[38;5;{num1}m{s}\033[0;0m\n")
    else:
        return(f"\033[38;5;{num1}m{s}\033[0;0m")


def construct_node_string(node: DrawNode):
    value = ""

    try:
        value = colors_256(str(node.node.value), node.node.color)
    except Exception:
        value = str(node.node.value)

    return "_" * node.extension_left + value + "_" * node.extension_right


def arrange_trees(*roots: DrawNode):
    left_boundary = LEFT_MARGIN

    for i in range(len(roots)):
        roots[i].move(left_boundary - roots[i].left_boundary)
        left_boundary = roots[i].right_boundary + 2

def draw(*roots ):
    draw_aux(*[DrawNode(root) for root in filter(lambda root: root, roots)])

def draw_aux(*roots: DrawNode):

    trees = [build_levels(root) for root in roots]

    arrange_trees(*roots)

    deepest = max([len(tree) for tree in trees])

    for level in range(deepest):

        position = 0
        line = ""
        for tree in trees:
            if level >= len(tree):
                continue

            for node in tree[level]:
                line += " " * (node.extended_position - position)
                line += construct_node_string(node)
                position = node.extended_position + get_len(node)

        print(line)


        edge_line = ""
        edge_position = 0
        for tree in trees:
            if level >= len(tree):
                continue

            for node in tree[level]:
                left = node.edges.left
                right = node.edges.right

                if left:
                    edge_line += " " * (left.position - edge_position)
                    edge_line += str(left)
                    edge_position = (left.position +1)

                if right:
                    edge_line += " " * (right.position - edge_position)
                    edge_line += str(right)
                    edge_position = (right.position +1)

        print(edge_line)

def main():
    pass

if __name__ == "__main__":
    main()
