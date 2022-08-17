"""Simple polygon builder methods."""

import math

from shapely.geometry import Polygon


def create_hexagon(edge: float, x: float, y: float):
    """
    Create a hexagon centered on (x, y)
    :param edge: length of the hexagon's edge
    :param x: x-coordinate of the hexagon's center
    :param y: y-coordinate of the hexagon's center
    :return: The polygon containing the hexagon's coordinates
    """
    c = [
        [x + math.cos(math.radians(angle)) * edge, y + math.sin(math.radians(angle)) * edge]
        for angle in range(0, 360, 60)
    ]
    return Polygon(c)


def create_square_tile(dim: float, x: float, y: float):
    """
    Create a tile of size dim*dim, centered on (x, y)
    :param dim: length of the tiles edges
    :param x: x-coordinate of the tile's center
    :param y: y-coordinate of the tile's center
    :return: The polygon
    """
    offset = dim / 2
    c = [
        (x + offset, y + offset),
        (x + offset, y - offset),
        (x - offset, y - offset),
        (x - offset, y + offset),
        (x + offset, y + offset),
    ]
    return Polygon(c)
