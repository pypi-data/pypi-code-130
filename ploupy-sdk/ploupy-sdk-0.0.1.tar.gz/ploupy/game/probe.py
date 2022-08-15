from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np

from ..models.core import GameConfig

from .entity import Entity

from ..models.game import ProbeState
from ..core import InvalidStateException

if TYPE_CHECKING:
    from .game import Game


class Probe(Entity):
    def __init__(self, state: ProbeState, game: Game) -> None:
        super().__init__()
        self._assert_complete_state(state)
        self._config = game.config
        self._id: str = state.id
        self._pos: np.ndarray = state.pos.pos
        self._target: np.ndarray | None = (
            None if state.target is None else state.target.coord
        )

    def _assert_complete_state(self, state: ProbeState):
        if None in (state.pos):
            raise InvalidStateException()

    @property
    def id(self) -> str:
        return self._id

    @property
    def pos(self) -> np.ndarray:
        return self._pos.copy()

    @property
    def target(self) -> np.ndarray:
        if self._target is None:
            return None
        return self._target.copy()

    async def _update_state(self, state: ProbeState):
        """
        Update instance with given state
        """
        if state.pos is not None:
            self._pos = state.pos.pos
        if state.target is not None:
            self._target = state.target.coord
        if state.death is not None:
            self._die(state.death)
