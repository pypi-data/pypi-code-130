from pydantic import BaseModel

from .core import Point


class JoinQueue(BaseModel):
    qid: str


class LeaveQueue(BaseModel):
    qid: str


class GameState(BaseModel):
    gid: str


class BuildFactory(BaseModel):
    coord: Point
    """Coordinate where to build the factory"""


class BuildTurret(BaseModel):
    coord: Point
    """Coordinate where to build the turret"""


class MoveProbes(BaseModel):
    ids: list[str]
    """List of the ids of each probe to move"""
    target: Point
    """Coordinate of the target"""


class ExplodeProbes(BaseModel):
    ids: list[str]
    """List of the ids of each probe to explode"""


class ProbesAttack(BaseModel):
    ids: list[str]
    """List of the ids of each probe that will attack"""
