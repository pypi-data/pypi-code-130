import json
import logging
import numpy as np
from pydantic import BaseModel

from .game.probe import Probe

from .core.exceptions import ActionFailedException

from .models import core as _c, actions as _a
from .sio import sio

logger = logging.getLogger("ploupy")


class Actions:
    @staticmethod
    async def _send_action(action: str, model: BaseModel):
        response = await sio.call(action, model.dict())
        response = _c.Response(**json.loads(response))

        if not response.success:
            logger.warning(f"{action} failed: {response.msg}")
            raise ActionFailedException(response.msg)

    @classmethod
    async def build_factory(cls, coord: _c.Pos):
        model = _a.BuildFactory(coord=_c.Point.from_list(coord))
        await cls._send_action("action_build_factory", model)

    @classmethod
    async def build_turret(cls, coord: _c.Pos):
        model = _a.BuildTurret(coord=_c.Point.from_list(coord))
        await cls._send_action("action_build_turret", model)

    @classmethod
    async def move_probes(cls, probes: list[Probe], target: _c.Pos):
        model = _a.MoveProbes(
            ids=[p.id for p in probes], target=_c.Point.from_list(target)
        )
        await cls._send_action("action_move_probes", model)

    @classmethod
    async def explode_probes(cls, probes: list[Probe]):
        model = _a.ExplodeProbes(ids=[p.id for p in probes])
        await cls._send_action("action_explode_probes", model)

    @classmethod
    async def probes_attack(cls, probes: list[Probe]):
        model = _a.ProbesAttack(ids=[p.id for p in probes])
        await cls._send_action("action_probes_attack", model)
