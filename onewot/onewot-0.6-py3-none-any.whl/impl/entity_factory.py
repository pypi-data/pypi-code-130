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
"""Basic implementation of an entity factory for WotBlitz entities."""

from __future__ import annotations

__all__: typing.Sequence[str] = ('EntityFactoryImpl',)

import typing

from onewot import clans as clan_models
from onewot import users as user_models
from onewot import achievements as achievement_models
from onewot import tournaments as tournament_models
from onewot import tanks as tank_models
from onewot import snowflakes
from onewot.api import entity_factory
from onewot.internal import unix

if typing.TYPE_CHECKING:
    from onewot.internal import data_binding


def calculate_win_percent(payload: data_binding.JSONObject) -> typing.Union[int, float]:
    battles = payload['statistics']['all']['battles']
    wins = payload['statistics']['all']['wins']

    try:
        percent = wins/battles * 100
    except ZeroDivisionError:
        return 0.0

    return round(percent, 2)


class EntityFactoryImpl(entity_factory.EntityFactory):
    """Standard implementation for a deserializer.

    This will convert objects from JSON compatible representations.
    """

    __slots__: typing.Sequence[str] = ()

    def deserialize_clan(self, payload: data_binding.JSONObject) -> clan_models.Clan:
        return clan_models.Clan(
            id=snowflakes.Snowflake(payload['clan_id']),
            created_at=unix.UnixTime(payload.get('created_at')),
            creator_id=snowflakes.Snowflake(payload.get('creator_id')),
            creator_name=payload.get('creator_name'),
            description=payload.get('description'),
            emblem_set_id=snowflakes.Snowflake(payload.get('emblem_set_id')),
            is_clan_disbanded=payload['is_clan_disbanded'],
            leader_id=snowflakes.Snowflake(payload.get('leader_id')),
            leader_name=payload.get('leader_name'),
            members_count=payload.get('members_count'),
            members_ids=payload.get('members_ids'),
            motto=payload.get('motto'),
            name=payload.get('name'),
            old_name=payload.get('old_name'),
            old_tag=payload.get('old_tag'),
            recruiting_policy=clan_models.RecruitingPolicy(
                payload.get('recruiting_policy')
            ) if not payload['is_clan_disbanded'] else None,
            renamed_at=payload.get('renamed_at'),
            tag=payload.get('tag'),
            updated_at=unix.UnixTime(payload['updated_at']),
            recruiting_options=self.deserialize_recruiting_options(
                payload['recruiting_options']
            )
        )

    def deserialize_user(self, payload: data_binding.JSONObject) -> user_models.User:
        return user_models.User(
            id=snowflakes.Snowflake(payload['account_id']),
            created_at=unix.UnixTime(payload['created_at']),
            last_battle_time=payload.get('last_battle_time'),
            nickname=payload['nickname'],
            updated_at=unix.UnixTime(payload['updated_at']),
            spotted=payload['statistics']['all']['spotted'],
            max_frags_tank_id=payload['statistics']['all']['max_frags_tank_id'],
            hits=payload['statistics']['all']['hits'],
            frags=payload['statistics']['all']['frags'],
            max_xp=payload['statistics']['all']['max_xp'],
            max_xp_tank_id=payload['statistics']['all']['max_xp_tank_id'],
            wins=payload['statistics']['all']['wins'],
            losses=payload['statistics']['all']['losses'],
            capture_points=payload['statistics']['all']['capture_points'],
            battles=payload['statistics']['all']['battles'],
            damage_dealt=payload['statistics']['all']['damage_dealt'],
            damage_received=payload['statistics']['all']['damage_received'],
            max_frags=payload['statistics']['all']['max_frags'],
            shots=payload['statistics']['all']['shots'],
            frags8p=payload['statistics']['all']['frags8p'],
            xp=payload['statistics']['all']['xp'],
            win_and_survived=payload['statistics']['all']['win_and_survived'],
            survived_battles=payload['statistics']['all']['survived_battles'],
            dropped_capture_points=payload['statistics']['all']['dropped_capture_points'],
            win_percent=calculate_win_percent(payload),
            achievements=payload['achievements'],
            rating=self.deserialize_user_rating(payload['statistics']['rating'])
        )

    def deserialize_achievement(self, payload: data_binding.JSONObject) -> typing.Type[type]:
        achievement = achievement_models.BaseAchievement(payload).make_class()
        payload = dict(payload['achievements'], max_series=payload['max_series'])
        return achievement(**payload)

    def deserialize_base_clan(self, payload: data_binding.JSONObject) -> clan_models.BaseClan:
        return clan_models.BaseClan(
            id=snowflakes.Snowflake(payload['clan_id']),
            created_at=unix.UnixTime(payload['created_at']),
            emblem_set_id=snowflakes.Snowflake(payload['emblem_set_id']),
            members_count=payload['members_count'],
            name=payload['name'],
            tag=payload['tag']
        )

    def deserialize_clan_member(self, payload: data_binding.JSONObject) -> user_models.ClanMember:
        return user_models.ClanMember(
            id=snowflakes.Snowflake(payload['account_id']),
            clan_id=snowflakes.Snowflake(payload['clan_id']),
            joined_at=unix.UnixTime(payload['joined_at']),
            role=user_models.MemberClanRole(payload['role']),
            clan=self.deserialize_base_clan(payload['clan']) if 'clan' in payload else None
        )

    def deserialize_recruiting_options(self, payload: data_binding.JSONObject) -> clan_models.RecruitingOptions:
        return clan_models.RecruitingOptions(
            vehicles_level=payload['vehicles_level'],
            wins_ratio=payload['wins_ratio'],
            average_battles_per_day=payload['average_battles_per_day'],
            battles=payload['battles'],
            average_damage=payload['average_damage']
        )

    def deserialize_tournament(self, payload: data_binding.JSONObject) -> tournament_models.Tournament:
        return tournament_models.Tournament(
            id=snowflakes.Snowflake(payload['tournament_id']),
            description=payload['description'],
            end_at=payload['end_at'],
            matches_start_at=unix.UnixTime(payload['matches_start_at']),
            registration_end_at=unix.UnixTime(payload['registration_end_at']),
            registration_start_at=unix.UnixTime(payload['registration_start_at']),
            start_at=unix.UnixTime(payload['start_at']),
            status=tournament_models.TournamentStatus(payload['status']),
            title=payload['title'],
            award=tournament_models.TournamentAward(
                amount=payload['award']['amount'],
                currency=tournament_models.CurrencyType(
                    payload['award']['currency']
                ) if payload['award']['currency'] else None
            ),
            fee=tournament_models.TournamentFee(
                amount=payload['fee']['amount'],
                currency=tournament_models.CurrencyType(
                    payload['fee']['currency']
                ) if payload['fee']['currency'] else None
            ),
            logo=tournament_models.TournamentLogo(**payload['logo']),
            winner_award=tournament_models.TournamentWinnerAward(
                amount=payload['winner_award']['amount'],
                currency=tournament_models.CurrencyType(
                    payload['winner_award']['currency']
                ) if payload['winner_award']['currency'] else None
            )
        )

    def deserialize_tank(self, payload: data_binding.JSONObject) -> tank_models.Tank:
        return tank_models.Tank(
            id=snowflakes.Snowflake(payload['tank_id']),
            name=payload['name'],
            description=payload['description'],
            engines=payload['engines'],
            guns=payload['guns'],
            is_premium=payload['is_premium'],
            nation=payload['nation'],
            next_tanks=payload['next_tanks'],
            prices_xp=payload['prices_xp'],
            suspensions=payload['suspensions'],
            tier=payload['tier'],
            turrets=payload['turrets'],
            type=payload['type'],
            cost=tank_models.TankCost(
                price_credit=payload['cost']['price_credit'],
                price_gold=payload['cost']['price_gold']
            ) if payload['cost'] is not None else None,
            default_profile=self.deserialize_tank_default_profile(payload['default_profile']),
            images=tank_models.TankImage(**payload['images']),
        )

    def deserialize_tank_default_profile(self, payload: data_binding.JSONObject) -> tank_models.DefaultProfile:
        return tank_models.DefaultProfile(
            battle_level_range_max=payload['battle_level_range_max'],
            battle_level_range_min=payload['battle_level_range_min'],
            engine_id=snowflakes.Snowflake(payload['engine_id']),
            firepower=payload['firepower'],
            gun_id=snowflakes.Snowflake(payload['gun_id']),
            hp=payload['hp'],
            hull_hp=payload['hull_hp'],
            hull_weight=payload['hull_weight'],
            is_default=payload['is_default'],
            maneuverability=payload['maneuverability'],
            max_ammo=payload['max_ammo'],
            max_weight=payload['max_weight'],
            profile_id=payload['profile_id'],
            protection=payload['protection'],
            shot_efficiency=payload['shot_efficiency'],
            signal_range=payload['signal_range'],
            speed_backward=payload['speed_backward'],
            speed_forward=payload['speed_forward'],
            suspension_id=snowflakes.Snowflake(payload['suspension_id']),
            turret_id=snowflakes.Snowflake(payload['turret_id']),
            weight=payload['weight'],
            armor=tank_models.DefaultArmor(
                hull=tank_models.ArmorHull(**payload['armor']['hull']),
                turret=tank_models.ArmorTurret(**payload['armor']['turret'])
            ),
            engine=tank_models.DefaultEngine(**payload['engine']),
            gun=tank_models.DefaultGun(**payload['gun']),
            shells=tuple(tank_models.DefaultShell(**shell) for shell in payload['shells']),
            suspension=tank_models.DefaultSuspension(**payload['suspension']),
            turret=tank_models.DefaultTurret(**payload['turret'])
        )

    def deserialize_user_rating(self, payload: data_binding.JSONObject) -> user_models.UserRating:
        return user_models.UserRating(
            battles=payload['battles'],
            calibration_battles_left=payload['calibration_battles_left'],
            capture_points=payload['capture_points'],
            current_season=payload['current_season'],
            damage_dealt=payload['damage_dealt'],
            damage_received=payload['damage_received'],
            dropped_capture_points=payload['dropped_capture_points'],
            frags=payload['frags'],
            frags8p=payload['frags8p'],
            hits=payload['hits'],
            is_recalibration=payload['is_recalibration'],
            losses=payload['losses'],
            mm_rating=payload['mm_rating'],
            recalibration_start_time=unix.UnixTime(payload['recalibration_start_time']),
            shots=payload['shots'],
            spotted=payload['spotted'],
            survived_battles=payload['survived_battles'],
            win_and_survived=payload['win_and_survived'],
            wins=payload['wins'],
            xp=payload['xp']
        )
