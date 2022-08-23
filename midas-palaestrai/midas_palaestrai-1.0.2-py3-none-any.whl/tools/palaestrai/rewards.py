import logging
import math
from typing import List

import numpy as np
from palaestrai.agent import (
    ActuatorInformation,
    RewardInformation,
    SensorInformation,
)
from palaestrai.types import Box, Discrete

from .reward import Reward

LOG = logging.getLogger(__name__)


def gauss_norm(
    raw_value: float,
    mu: float = 1,
    sigma: float = 0.1,
    c: float = 0.5,
    a: float = -1,
):
    if not isinstance(raw_value, float):
        try:
            raw_value = sum(raw_value)
        except TypeError:
            return 0
    gaus_reward = a * math.exp(-((raw_value - mu) ** 2) / (2 * sigma**2)) - c
    return gaus_reward


class NoExtGridHealthReward(Reward):
    def __init__(self, **params):
        super().__init__(**params)
        self.grid_health_sensor = params.get(
            "grid_health", "Powergrid-0.Grid-0.health"
        )
        self.ext_grid_sensor = params.get(
            "ext_grid", "Powergrid-0.0-ext_grid-0.p_mw"
        )

    def __call__(self, state, *args, **kwargs):

        rewards = []
        for sensor in state:
            if self.grid_health_sensor == sensor.sensor_id:
                system_health_reward = RewardInformation(
                    sensor.sensor_value, Discrete(2), "grid_health_reward"
                )
                rewards.append(system_health_reward)
            elif self.ext_grid_sensor in sensor.sensor_id:
                reward = abs(sensor.sensor_value)
                external_grid_penalty_reward = RewardInformation(
                    reward, Discrete(1000), "external_grid_penalty_reward"
                )
                rewards.append(external_grid_penalty_reward)
        return rewards


class GridHealthReward(Reward):
    def _line_load(self, value):
        if not isinstance(value, int):
            return 0
        if value <= 100:
            return 0
        if value > 100 and value <= 120:
            return value - 100
        if value > 120:
            return np.exp((value - 100) / 10)

    def __call__(
        self, state: List[SensorInformation], *arg, **kwargs
    ) -> List[ActuatorInformation]:

        reward = 0
        for sensor in state:
            if "vm_pu" in sensor.sensor_id:
                reward += (gauss_norm(sensor(), 1, 0.02, 1.0, 2)) * 50
            if "line-" in sensor.sensor_id:
                reward -= self._line_load(sensor())
        final_reward = RewardInformation(
            reward, Box(-np.inf, np.inf, shape=(1,)), "grid_health_reward"
        )
        return [final_reward]


class ExtendedGridHealthReward(Reward):
    def __call__(
        self, state: List[SensorInformation], *args, **kwargs
    ) -> List[RewardInformation]:
        voltages = np.sort(
            np.array([s() for s in state if "vm_pu" in s.sensor_id]),
            axis=None,
        )
        voltage_rewards = [
            RewardInformation(
                voltages[0],
                Box(0.8, 1.2, shape=(1,)),
                reward_id="vm_pu-min",
            ),
            RewardInformation(
                voltages[-1],
                Box(0.8, 1.2, shape=(1,)),
                reward_id="vm_pu-max",
            ),
            RewardInformation(
                voltages[len(voltages) // 2],
                Box(0.8, 1.2, shape=(1,)),
                reward_id="vm_pu-median",
            ),
            RewardInformation(
                voltages.mean(),
                Box(0.8, 1.2, shape=(1,)),
                reward_id="vm_pu-mean",
            ),
            RewardInformation(
                voltages.std(),
                Box(0.8, 1.2, shape=(1,)),
                reward_id="vm_pu-std",
            ),
        ]

        lineloads = np.sort(
            np.array(
                [s() for s in state if ".loading_percent" in s.sensor_id]
            ),
            axis=None,
        )
        lineload_rewards = [
            RewardInformation(
                lineloads[0],
                Box(0.0, 100.0, shape=(1,)),
                reward_id="lineload-min",
            ),
            RewardInformation(
                lineloads[-1],
                Box(0.0, 100.0, shape=(1,)),
                reward_id="lineload-max",
            ),
            RewardInformation(
                lineloads[len(lineloads) // 2],
                Box(0.0, 100.0, shape=(1,)),
                reward_id="lineload-median",
            ),
            RewardInformation(
                lineloads.mean(),
                Box(0.0, 100.0, shape=(1,)),
                reward_id="lineload-mean",
            ),
            RewardInformation(
                lineloads.std(),
                Box(0.0, 100.0, shape=(1,)),
                reward_id="lineload-std",
            ),
        ]

        return voltage_rewards + lineload_rewards


class AllesDestroyAllPire2RewardIchWeissNicht(Reward):
    def __call__(
        self, state: List[SensorInformation], *args, **kwargs
    ) -> List[RewardInformation]:

        points = 0
        # vm_pus = np.array([s() for s in state if "vm_pu" in s.sensor_id])

        # line_loads = np.array([s() for s in state if ".loading_percent" in s.sensor_id])
        # out_of_service_lines = 0
        # out_of_service_loads = 0
        # out_of_service_sgens = 0

        min_reward = 0
        max_reward = 0
        ppoints = 0
        npoints = 0
        for s in state:
            if "line" in s.sensor_id:
                if "in_service" in s.sensor_id:
                    min_reward -= 10
                    max_reward += 1
                    if s():
                        points += 1
                    else:
                        points -= 10

                if ".loading_percent" in s.sensor_id:
                    min_reward -= 10
                    max_reward += 1
                    if s() < 95:
                        points += 1
                    elif s() < 100:
                        points -= 1
                    else:
                        points -= 10

            if "load-" in s.sensor_id:
                if "in_service" in s.sensor_id:
                    min_reward -= 10
                    max_reward += 1
                    if s():
                        points += 1
                    else:
                        points -= 10

            if "sgen-" in s.sensor_id:
                if "in_service" in s.sensor_id:
                    min_reward -= 10
                    max_reward += 1
                    if s():
                        points += 1
                    else:
                        points -= 10

            if "bus" in s.sensor_id:
                if "vm_pu" in s.sensor_id:
                    min_reward -= 10
                    max_reward += 1
                    if 0.95 <= s() <= 1.05:
                        points += 1
                    elif 0.9 <= s() <= 1.1:
                        points -= 5
                    else:
                        points -= 10

            if "trafo" in s.sensor_id:
                if "loading_percent" in s.sensor_id:
                    min_reward -= 10
                    max_reward += 1
                    if s() < 95:
                        points += 1
                    elif s() < 100:
                        points -= 1
                    else:
                        points -= 10

        extgrid_rew = ExtendedGridHealthReward()
        rewards = extgrid_rew(state)

        rewards.append(
            RewardInformation(
                points,
                Box(min_reward, max_reward, (1,), np.int64),
                reward_id="ErikaReward",
            )
        )
        LOG.critical(points)
        return rewards
