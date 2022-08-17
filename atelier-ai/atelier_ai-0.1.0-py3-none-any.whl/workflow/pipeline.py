#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# ================================================================================================ #
# Project    : Atelier AI: Studio for AI Designers                                                 #
# Version    : 0.1.0                                                                               #
# Python     : 3.10.4                                                                              #
# Filename   : /pipeline.py                                                                        #
# ------------------------------------------------------------------------------------------------ #
# Author     : John James                                                                          #
# Email      : john.james.ai.studio@gmail.com                                                      #
# URL        : https://github.com/john-james-ai/atelier-ai                                         #
# ------------------------------------------------------------------------------------------------ #
# Created    : Thursday August 11th 2022 09:43:52 pm                                               #
# Modified   : Tuesday August 16th 2022 10:05:26 pm                                                #
# ------------------------------------------------------------------------------------------------ #
# License    : BSD 3-clause "New" or "Revised" License                                             #
# Copyright  : (c) 2022 John James                                                                 #
# ================================================================================================ #
"""Pipeline Module"""
import os
from abc import ABC, abstractmethod
import importlib
from datetime import datetime
import pandas as pd
import mlflow
import logging

from atelier.data.io import IOFactory
from atelier.workflow.operators import Operator

# ------------------------------------------------------------------------------------------------ #
logging.getLogger(__name__).addHandler(logging.NullHandler())
# ------------------------------------------------------------------------------------------------ #


class Pipeline(ABC):
    """Base class for Pipelines

    Args:
        name (str): Human readable name for the pipeline run.
        context (dict): Data required by all operators in the pipeline. Optional.
    """

    def __init__(self, name: str, context: dict = {}) -> None:
        self._name = name
        self._context = context
        self._steps = []
        self._active_run = None
        self._run_id = None

        self._created = datetime.now()
        self._started = None
        self._stopped = None
        self._duration = None

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def steps(self) -> list:
        return self._steps

    @property
    def created(self) -> datetime:
        return self._created

    @property
    def started(self) -> datetime:
        return self._started

    @property
    def stopped(self) -> datetime:
        return self._stopped

    @property
    def duration(self) -> datetime:
        return self._duration

    def set_steps(self, steps: []) -> None:
        """Sets the steps on the Pipeline object.

        Args:
            steps (dict): List of pipeline steps
        """
        self._steps = steps

    def print_steps(self) -> None:
        """Prints the steps in the order in which they were added."""
        steps = {
            "Seq": list(range(1, len(self._steps) + 1)),
            "Step": [step.name for step in self._steps.values()],
            "Created": [step.created for step in self._steps.values()],
            "Started": [step.started for step in self._steps.values()],
            "Stopped": [step.stopped for step in self._steps.values()],
            "Duration": [step.duration for step in self._steps.values()],
            "Force": [step.force for step in self._steps.values()],
            "Status": [step.status for step in self._steps.values()],
        }
        df = pd.DataFrame(steps)
        print(df)

    def run(self) -> None:
        """Runs the pipeline"""
        self._setup()
        self._execute(context=self._context)
        self._teardown()

    @abstractmethod
    def _execute(self, context: dict = {}) -> None:
        """Iterates through the sequence of steps.

        Args:
            context (dict): Dictionary of parameters shared across steps.
        """

    def _setup(self) -> None:
        """Executes setup for pipeline."""
        mlflow.start_run()
        self._active_run = mlflow.active_run()
        self._run_id = self._active_run.info.run_id
        self._started = datetime.now()

    def _teardown(self) -> None:
        """Completes the pipeline process."""
        mlflow.end_run()
        self._stopped = datetime.now()
        self._duration = round((self._stopped - self._started).total_seconds(), 4)

    def _update_step(self, step: Operator) -> None:
        self._steps[step.name] = step


# ------------------------------------------------------------------------------------------------ #


class DataPipe(Pipeline):
    def __init__(self, name: str, context: dict = {}) -> None:
        super(DataPipe, self).__init__(name=name, context=context)

    def __str__(self) -> str:
        return f"DataPipe {self._name}"

    def __repr__(self):
        return f"DataPipe(name={self._name})"

    def _execute(self, context: dict = {}) -> None:
        """Iterates through the sequence of steps.

        Args:
            context (dict): Dictionary of parameters shared across steps.
        """
        data = None
        for step in self._steps.values():
            result = step.run(data=data, context=context)
            data = result if result is not None else data
            self._update_step(step=step)


# ------------------------------------------------------------------------------------------------ #


class PipelineBuilder(ABC):
    """Constructs Configuration file based Pipeline objects"""

    def reset(self) -> None:
        self._pipeline = None

    @property
    def pipeline(self) -> Pipeline:
        return self._pipeline

    def build(self, config_filepath: str) -> None:
        """Constructs a Pipeline object.

        Args:
            config_filepath (str): Pipeline configuration
        """
        config = self._get_config(config_filepath)
        pipeline = self.build_pipeline(config)
        steps = self._build_steps(config.get("steps", None))
        pipeline.set_steps(steps)
        self._pipeline = pipeline

    def _get_config(self, config_filepath: str) -> dict:
        fileformat = os.path.splitext(config_filepath)[1].replace(".", "")
        io = IOFactory.io(fileformat=fileformat)
        return io.read(config_filepath)

    @abstractmethod
    def build_pipeline(self, config: dict) -> Pipeline:
        """Delegated to subclasses."""

    def _build_steps(self, config: dict) -> list:
        """Iterates through task and returns a list of task objects."""

        steps = {}

        for _, step_config in config.items():

            try:

                # Create task object from string using importlib
                module = importlib.import_module(name=step_config["module"])
                step = getattr(module, step_config["operator"])

                operator = step(
                    name=step_config["name"],
                    params=step_config["params"],
                )

                steps[operator.name] = operator

            except KeyError as e:
                logging.error("Configuration File is missing operator configuration data")
                raise (e)

        return steps


# ------------------------------------------------------------------------------------------------ #
class DataPipeBuilder(PipelineBuilder):
    """Constructs a data processing pipeline."""

    def __init__(self) -> None:
        self._config_filepath = None
        self.reset()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    def build_pipeline(self, config: dict) -> DataPipe:
        return DataPipe(name=config.get("name"))
