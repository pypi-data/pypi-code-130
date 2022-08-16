"""Logic for fabric bin packing search."""
from __future__ import annotations

import math
from typing import List

from rectpack import newPacker

MATERIAL_WIDTH = 66
INCHES_IN_YARD = 36


def check_answer(rectangles: List[tuple[int, int]], yards: int) -> tuple[bool, int]:
    """Checks if right answer is found.

    >>> rectangles = [(10,10), (20,20)]
    >>> yards = 2
    >>> check_answer(rectangles, yards)
    (False, 1)
    >>> check_answer(rectangles, yards)
    (True, 1)

    Args:
        rectangles (List[tuple[int,int]): List of tuples in form of [(x, y)]
    """
    initial = bin_packing_calculator(rectangles, calc_material_dimensions(yards))
    # 1 yard is the min amount of fabric and attempting 0 yards on bin packing will cause error
    if yards == 1 and initial == 1:
        return True, initial
    lower = bin_packing_calculator(rectangles, calc_material_dimensions(yards - 1))

    return initial == 1 and lower > initial, initial


def calc_material_dimensions(yards):
    return MATERIAL_WIDTH, yard_to_inches(yards)


def bin_packing_calculator(rectangles, material):
    """Bin packing algorthm."""
    # behavior seems reverse, when rotation is turned off it allows rotation
    packer = newPacker(rotation=True)
    for rectangle in rectangles:
        packer.add_rect(*rectangle)
    # inf count means it will add bins as required
    packer.add_bin(*material, count=float("inf"))
    packer.pack()
    return len(packer)


def max_size(rectangles: tuple) -> int:
    """Get maximum length of all rectangles side by side"""
    return sum(map(lambda rectangle: max(rectangle), rectangles))


def inches_to_yards(inches: int) -> int:
    """Convert inches to yards."""
    return math.ceil(inches / INCHES_IN_YARD)


def yard_to_inches(yards: int) -> int:
    """Convert years to inches."""
    return yards * INCHES_IN_YARD


def get_median(search_space: tuple[int, int]):
    """Get middle int in search space."""
    assert search_space[1] >= search_space[0]
    difference = search_space[1] - search_space[0]
    middle = difference // 2
    return search_space[0] + middle


def redefine_search_space(search_space: List[int], median: int, result: int):
    """Cut search space in half."""
    if result == 1:
        search_space[1] = median
    else:
        search_space[0] = median

    return search_space


def binary_seach(rectangles, search_space=None) -> int:
    """Implements Binary Search."""
    if search_space is None:
        # initial search space is 1 yard, to maximum value
        # assumes that the length of the shortest side is less than MATERIAL_WIDTH
        search_space = [1, max_size(rectangles) + 1]
    median = get_median(search_space)
    check, result = check_answer(rectangles, median)
    if check is True:
        return median
    search_space = redefine_search_space(search_space, median, result)
    return binary_seach(rectangles, search_space)


def combine_rectangles(data: List[tuple[int, int, int]]) -> List:
    """Combine list of rectangles to"""
    rectangles = []
    for d in data:
        rectangles.extend([d[:2]] * d[2])
    return rectangles


def calculate(data: List[tuple[int, int, int]]) -> int:
    """Get number of yards of fabric for tackboards."""
    rectangles = combine_rectangles(data)
    # rotate_rectangles(rectangles)
    return binary_seach(rectangles)


if __name__ == "__main__":
    example_data = [
        (30, 40, 10),
    ]
    print(calculate(example_data))
