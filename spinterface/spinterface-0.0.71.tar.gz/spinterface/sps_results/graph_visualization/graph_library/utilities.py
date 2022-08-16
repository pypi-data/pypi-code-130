r"""
Utilities for Graph Visualizations
"""
from typing import List, Tuple

import numpy as np


def make_multiline_text(lines: List[str]) -> str:
    r"""
    Formats a couple of strings, concatenate them and return a single string
    """
    str = '<b>' + lines[0] + '</b><br>'
    for line in lines[1:-1]:
        str = str + line + '<br>'
    str = str + lines[-1]
    return str


def distribute_around_node(parent_node_pos: Tuple[float,float], opening_angle: float, distances_child_parent: List[float]) -> Tuple[List[Tuple[float,float]],List[np.ndarray]]:
    r"""

    :param parent_node_pos:
    :param opening_angle:
    :param distances_child_parent:
    :return: positions of childs, and relative directions to parent of childs
    """
    r = np.linalg.norm(np.array([parent_node_pos[0],parent_node_pos[1]]))
    # Calculate phi0 angle
    phi0 = np.arctan2(parent_node_pos[1], parent_node_pos[0])
    # Input angle deg -> rad
    opening_angle = opening_angle * np.pi / 180
    # Angle between child nodes
    dangle_childs = opening_angle / len(distances_child_parent)
    # Anlge shift
    shift_angle = phi0 - opening_angle / 2
    positions = []
    directions = []
    for index,d_child in enumerate(distances_child_parent):
        x = d_child * np.cos(dangle_childs * index + shift_angle)
        y = d_child * np.sin(dangle_childs * index + shift_angle)
        positions.append((x + parent_node_pos[0],y + parent_node_pos[0]))
        vec = np.array([positions[index][0]-parent_node_pos[0],positions[index][1]-parent_node_pos[1]])
        directions.append(vec / np.linalg.norm(vec))
    return positions, directions