from dataclasses import dataclass

from tsk import utils


@dataclass
class Tasklist:
    """Models a tasklist - a container for tasks."""

    title: str
    id: str = utils.get_id()
