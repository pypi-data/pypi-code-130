from pydantic import BaseModel

from .core import Point, GameConfig


class TileState(BaseModel):
    id: str
    coord: Point | None = None
    owner: str | None = None
    """Only store the username of the owner"""
    occupation: int | None = None


class FactoryState(BaseModel):
    id: str
    coord: Point | None = None
    death: str | None = None


class ProbeState(BaseModel):
    id: str
    pos: Point | None = None
    death: str | None = None
    target: Point | None = None


class TurretState(BaseModel):
    id: str
    coord: Point | None = None
    death: str | None = None
    shot_id: str | None = None


class MapState(BaseModel):
    tiles: list[TileState] = []


class PlayerState(BaseModel):
    uid: str
    username: str
    money: int | None = None
    death: str | None = None
    income: int | None = None
    factories: list[FactoryState] = []
    turrets: list[TurretState] = []
    probes: list[ProbeState] = []


class GameState(BaseModel):
    gid: str
    config: GameConfig | None = None
    map: MapState | None = None
    players: list[PlayerState] = []
