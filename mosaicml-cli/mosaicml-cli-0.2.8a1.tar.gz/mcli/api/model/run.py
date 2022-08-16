""" GraphQL representation of MCLIJob"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from mcli.api.engine.utils import dedent_indent
from mcli.api.schema.generic_model import DeserializableModel
from mcli.models.run_config import FinalRunConfig
from mcli.utils.utils_run_status import RunStatus


@dataclass
class Run(DeserializableModel):
    """The GraphQL Serializable and Deserializable representation of a Run

    The intermediate form includes both the RunInput and MCLIJob as a bjson value
    """

    run_uid: str
    name: str
    status: RunStatus
    created_at: datetime
    updated_at: datetime
    config: FinalRunConfig
    job_config: dict

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    property_translations = {
        'runUid': 'run_uid',
        'runName': 'name',
        'runStatus': 'status',
        'createdAt': 'created_at',
        'updatedAt': 'updated_at',
        'startedAt': 'started_at',
        'completedAt': 'completed_at',
        'runInput': 'config',
        'jobConfig': 'job_config',
    }


def get_run_schema(indentation: int = 2,):
    """ Get the GraphQL schema for a :type RunModel:
    Args:
        indentation (int): Optional[int] for the indentation of the block
    Returns:
        Returns a GraphQL string with all the fields needed to initialize a
        :type RunModel:
    """
    return dedent_indent("""
runUid
runName
runInput
runStatus
createdAt
updatedAt
jobConfig
        """, indentation)
