from typing import Tuple


def coordinates_to_java_description(coordinates: Tuple[str, ...]) -> str:
    return "@".join(reversed(coordinates))
