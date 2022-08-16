from typing import Iterable, NoReturn, Union

from .base_hierarchy import BaseHierarchyBound
from .coordinates import HierarchyCoordinates


def raise_multiple_levels_with_same_name_error(
    level_name: str,
    *,
    hierarchies: Union[Iterable[HierarchyCoordinates], Iterable[BaseHierarchyBound]],
) -> NoReturn:
    raise KeyError(
        f"""Multiple levels are named {level_name}. Specify the hierarchy (and the dimension if necessary): {", ".join([
            f'cube.levels["{hierarchy[0]}", "{hierarchy[1]}", "{level_name}"]' if isinstance(hierarchy, tuple) else f'cube.levels["{hierarchy.dimension}", "{hierarchy.name}", "{level_name}"]'
            for hierarchy in hierarchies
        ])}"""
    )
