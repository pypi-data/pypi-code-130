from __future__ import annotations
from typing import TYPE_CHECKING

from ..models.core import GameConfig, Pos
from ..models.game import MapState

from .tile import Tile

if TYPE_CHECKING:
    from .game import Game


class Map:
    def __init__(self, state: MapState, game: Game) -> None:
        self._config: GameConfig = game.config
        self._map_tiles: dict[str, Tile] = {s.id: Tile(s, game) for s in state.tiles}
        self._matrix_tiles: list[list[Tile]] = self._build_matrix_tiles()

    def _build_matrix_tiles(self) -> list[list[Tile]]:
        x, y = self._config.dim.coord
        matrix = [[None for _ in range(y)] for _ in range(x)]

        for tile in self._map_tiles.values():
            matrix[tile.coord[0]][tile.coord[1]] = tile
        return matrix

    @property
    def tiles(self) -> list[Tile]:
        return list(self._map_tiles.values())

    def get_tile(self, coord: Pos) -> Tile | None:
        """
        Return the tile at the given coord, if it exists
        """
        x, y = coord
        if x < 0 or y < 0 or x >= self._config.dim.x or y >= self._config.dim.y:
            return None
        return self._matrix_tiles[x][y]

    async def _update_state(self, state: MapState):
        """
        Update instance with given state
        """
        for ts in state.tiles:
            tile = self._map_tiles.get(ts.id)
            if tile is not None:
                await tile._update_state(ts)
