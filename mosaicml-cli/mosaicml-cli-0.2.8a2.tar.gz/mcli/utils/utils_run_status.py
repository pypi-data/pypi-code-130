"""Utilities for interpreting pod status"""
from __future__ import annotations

import functools
from dataclasses import dataclass
from enum import Enum, EnumMeta
from typing import Any, Dict, List, Set, Type, TypeVar

from kubernetes import client

from mcli.utils.utils_kube import deserialize

__all__ = ['RunStatus']


class StatusMeta(EnumMeta):
    """Metaclass for RunStatus that adds some useful class properties
    """

    @property
    def failed_states(cls) -> Set[RunStatus]:
        return {RunStatus.FAILED, RunStatus.FAILED_PULL, RunStatus.TERMINATING, RunStatus.STOPPED, RunStatus.STOPPING}

    @property
    def order(cls) -> List[RunStatus]:
        """Order of pod states, from latest to earliest
        """
        return [
            RunStatus.TERMINATING,
            RunStatus.FAILED,
            RunStatus.FAILED_PULL,
            RunStatus.STOPPED,
            RunStatus.STOPPING,
            RunStatus.COMPLETED,
            RunStatus.RUNNING,
            RunStatus.STARTING,
            RunStatus.SCHEDULED,
            RunStatus.QUEUED,
            RunStatus.PENDING,
            RunStatus.UNKNOWN,
        ]


@functools.total_ordering
class RunStatus(Enum, metaclass=StatusMeta):
    """Enum for possible pod states
    """
    PENDING = 'PENDING'
    SCHEDULED = 'SCHEDULED'
    QUEUED = 'QUEUED'
    STARTING = 'STARTING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    STOPPING = 'STOPPING'
    STOPPED = 'STOPPED'
    FAILED_PULL = 'FAILED_PULL'
    FAILED = 'FAILED'
    TERMINATING = 'TERMINATING'
    UNKNOWN = 'UNKNOWN'

    def __lt__(self, other: RunStatus):
        if not isinstance(other, RunStatus):
            raise TypeError(f'Cannot compare order of ``RunStatus`` and {type(other)}')
        return RunStatus.order.index(self) > RunStatus.order.index(other)

    def before(self, other: RunStatus, inclusive: bool = False) -> bool:
        """Returns True if this state usually comes "before" the other

        Args:
            other: Another RunStatus
            inclusive: If True, == evaluates to True. Default False.

        Returns:
            True of this state is "before" the other

        Examples:
        > RunStatus.RUNNING.before(RunStatus.COMPLETED)
        True

        > RunStatus.PENDING.before(RunStatus.RUNNING)
        True
        """
        return (self < other) or (inclusive and self == other)

    def after(self, other: RunStatus, inclusive: bool = False) -> bool:
        """Returns True if this state usually comes "after" the other

        Args:
            other: Another RunStatus
            inclusive: If True, == evaluates to True. Default False.

        Returns:
            True of this state is "after" the other

        Examples:
        > RunStatus.RUNNING.before(RunStatus.COMPLETED)
        True

        > RunStatus.PENDING.before(RunStatus.RUNNING)
        True
        """
        return (self > other) or (inclusive and self == other)


def cli_parse_run_status(text: str) -> str:
    """Parse an argument into a normalized string to match against RunStatus values

    Args:
        text: Argument string that should match a status value (e.g. pending)

    Returns:
        Normalized string
    """
    return text.title().replace('_', '').lower()


# pylint: disable-next=invalid-name
CLI_STATUS_OPTIONS = [cli_parse_run_status(state.value) for state in RunStatus]

StatusType = TypeVar('StatusType')  # pylint: disable=invalid-name


@dataclass
class PodStatus():
    """Base pod status detector
    """
    state: RunStatus
    message: str = ''
    reason: str = ''

    @classmethod
    def from_pod_dict(cls: Type[PodStatus], pod_dict: Dict[str, Any]) -> PodStatus:
        """Get the status of a pod from its dictionary representation

        This is useful if the pod has already been converted to a JSON representation

        Args:
            pod_dict: Dictionary representation of a V1Pod object

        Returns:
            PodStatus instance
        """
        if 'status' not in pod_dict:
            raise KeyError('pod_dict must have a valid "status" key')
        pod = deserialize(pod_dict, 'V1Pod')
        return cls.from_pod(pod)

    @classmethod
    def _pending_phase_match(cls: Type[PodStatus], pod: client.V1Pod) -> PodStatus:

        # Scheduled or queuing
        conditions = pod.status.conditions if pod.status.conditions else []
        if conditions:
            scheduled_condition = [c for c in conditions if c.type == 'PodScheduled'][0]
            if scheduled_condition.status == 'True' and len(conditions) == 1:
                return PodStatus(state=RunStatus.SCHEDULED)
            elif scheduled_condition.status == 'False' and scheduled_condition.reason == 'Unschedulable':
                return PodStatus(state=RunStatus.QUEUED)

        # Attempting to start container
        container_statuses = pod.status.container_statuses if pod.status.container_statuses else []
        if container_statuses:
            waiting = container_statuses[0].state.waiting
            if waiting and 'ContainerCreating' in waiting.reason:
                return PodStatus(state=RunStatus.STARTING)
            elif waiting and waiting.reason in {'ErrImagePull', 'ImagePullBackOff'}:
                return PodStatus(state=RunStatus.FAILED_PULL)

        # Else generic pending
        return PodStatus(state=RunStatus.PENDING)

    @classmethod
    def _running_phase_match(cls: Type[PodStatus], pod: client.V1Pod) -> PodStatus:
        del pod
        return PodStatus(state=RunStatus.RUNNING)

    @classmethod
    def _completed_phase_match(cls: Type[PodStatus], pod: client.V1Pod) -> PodStatus:
        del pod
        return PodStatus(state=RunStatus.COMPLETED)

    @classmethod
    def _failed_phase_match(cls: Type[PodStatus], pod: client.V1Pod) -> PodStatus:
        container_statuses = pod.status.container_statuses or []
        if container_statuses:
            terminated = container_statuses[0].state.terminated
            if terminated and terminated.exit_code == 137:
                return PodStatus(state=RunStatus.STOPPED)
        return PodStatus(state=RunStatus.FAILED)

    @classmethod
    def _unknown_phase_match(cls: Type[PodStatus], pod: client.V1Pod) -> PodStatus:
        del pod
        return PodStatus(state=RunStatus.UNKNOWN)

    @classmethod
    def from_pod(cls: Type[PodStatus], pod: client.V1Pod) -> PodStatus:
        """Get the appropriate PodStatus instance from a Kubernetes V1PodStatus object

        The resulting PodStatus instance contains parsed information about the current state of the pod

        Args:
            status: Valid V1PodStatus object

        Returns:
            PodStatus instance
        """

        if getattr(pod.metadata, 'deletion_timestamp', None) is not None:
            return PodStatus(state=RunStatus.TERMINATING)

        if pod.status.phase == 'Pending':
            return cls._pending_phase_match(pod)
        elif pod.status.phase == 'Running':
            return cls._running_phase_match(pod)
        elif pod.status.phase == 'Succeeded':
            return cls._completed_phase_match(pod)
        elif pod.status.phase == 'Failed':
            return cls._failed_phase_match(pod)
        else:
            return cls._unknown_phase_match(pod)
