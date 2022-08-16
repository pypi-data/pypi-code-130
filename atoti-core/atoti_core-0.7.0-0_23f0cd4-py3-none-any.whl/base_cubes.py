from dataclasses import dataclass
from typing import Mapping, TypeVar

from .base_cube import BaseCubeBound
from .keyword_only_dataclass import keyword_only_dataclass
from .repr_json import ReprJson, ReprJsonable

CubeT = TypeVar("CubeT", bound=BaseCubeBound, covariant=True)


@keyword_only_dataclass
# See https://github.com/python/mypy/issues/5374.
@dataclass(frozen=True)  # type: ignore[misc]
class BaseCubes(Mapping[str, CubeT], ReprJsonable):
    """Manage the cubes of the session."""

    def _repr_json_(self) -> ReprJson:
        """Return the JSON representation of cubes."""
        return (
            {name: cube._repr_json_()[0] for name, cube in sorted(self.items())},
            {"expanded": False, "root": "Cubes"},
        )


BaseCubesBound = BaseCubes[BaseCubeBound]
