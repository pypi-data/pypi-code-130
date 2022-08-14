# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2022 Crisp Crow
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Entities that are used to describe tanks on WotBlitz."""

from __future__ import annotations

__all__: typing.Sequence[str] = ('Tank',)

import typing

import attr

if typing.TYPE_CHECKING:
    from onewot import snowflakes


@attr.define(slots=True, frozen=True)
class Tank:
    id: snowflakes.Snowflake = attr.field()
    name: str = attr.field()
    description: str = attr.field()
    engines: list[snowflakes.Snowflake] = attr.field()
    guns: list[snowflakes.Snowflake] = attr.field()
    is_premium: bool = attr.field()
    nation: str = attr.field()
    next_tanks: dict[snowflakes.Snowflake, int] = attr.field()
    prices_xp: dict[snowflakes.Snowflake, int] = attr.field()
    suspensions: list[snowflakes.Snowflake] = attr.field()
    tier: int = attr.field()
    turrets: list[snowflakes.Snowflake] = attr.field()
    type: str = attr.field()
    cost: TankCost = attr.field()
    default_profile: DefaultProfile = attr.field()
    images: TankImage = attr.field()


@attr.define(slots=True, frozen=True)
class DefaultEngine:
    name: str = attr.field()
    fire_chance: int = attr.field()
    power: int = attr.field()
    tier: int = attr.field()
    weight: int = attr.field()


@attr.define(slots=True, frozen=True)
class DefaultGun:
    name: str = attr.field()
    aim_time: float = attr.field()
    caliber: int = attr.field()
    clip_capacity: int = attr.field()
    clip_reload_time: float = attr.field()
    dispersion: float = attr.field()
    fire_rate: float = attr.field()
    move_down_arc: int = attr.field()
    move_up_arc: int = attr.field()
    reload_time: int = attr.field()
    tier: int = attr.field()
    traverse_speed: int = attr.field()
    weight: int = attr.field()


@attr.define(slots=True, frozen=True)
class DefaultSuspension:
    name: str = attr.field()
    load_limit: int = attr.field()
    tier: int = attr.field()
    traverse_speed: int = attr.field()
    weight: int = attr.field()


@attr.define(slots=True, frozen=True)
class DefaultTurret:
    name: str = attr.field()
    hp: int = attr.field()
    tier: int = attr.field()
    traverse_left_arc: int = attr.field()
    traverse_right_arc: int = attr.field()
    traverse_speed: int = attr.field()
    view_range: int = attr.field()
    weight: int = attr.field()


@attr.define(slots=True, frozen=True)
class TankCost:
    price_credit: int = attr.field()
    price_gold: int = attr.field()


@attr.define(slots=True, frozen=True)
class DefaultProfile:
    battle_level_range_max: int = attr.field()
    battle_level_range_min: int = attr.field()
    engine_id: snowflakes.Snowflake = attr.field()
    firepower: int = attr.field()
    gun_id: snowflakes.Snowflake = attr.field()
    hp: int = attr.field()
    hull_hp: int = attr.field()
    hull_weight: int = attr.field()
    is_default: bool = attr.field()
    maneuverability: int = attr.field()
    max_ammo: int = attr.field()
    max_weight: int = attr.field()
    profile_id: str = attr.field()
    protection: int = attr.field()
    shot_efficiency: int = attr.field()
    signal_range: int = attr.field()
    speed_backward: int = attr.field()
    speed_forward: int = attr.field()
    suspension_id: snowflakes.Snowflake = attr.field()
    turret_id: snowflakes.Snowflake = attr.field()
    weight: int = attr.field()
    armor: DefaultArmor = attr.field()
    engine: DefaultEngine = attr.field()
    gun: DefaultGun = attr.field()
    shells: DefaultShell = attr.field()
    suspension: DefaultSuspension = attr.field()
    turret: DefaultTurret = attr.field()


@attr.define(slots=True, frozen=True)
class ArmorType:
    front: int = attr.field()
    rear: int = attr.field()
    sides: int = attr.field()


@attr.define(slots=True, frozen=True)
class ArmorTurret(ArmorType):
    ...


@attr.define(slots=True, frozen=True)
class ArmorHull(ArmorType):
    ...


@attr.define(slots=True, frozen=True)
class DefaultArmor:
    hull: ArmorHull = attr.field()
    turret: ArmorTurret = attr.field()


@attr.define(slots=True, frozen=True)
class DefaultShell:
    damage: int = attr.field()
    penetration: int = attr.field()
    type: str = attr.field()


@attr.define(slots=True, frozen=True)
class TankImage:
    preview: str = attr.field()
    normal: str = attr.field()
