"""Implements the stop_runs API for Kubernetes"""
from __future__ import annotations

from concurrent.futures import Future, as_completed
from http import HTTPStatus
from typing import Dict, List, Optional, Union, overload

from kubernetes.client.exceptions import ApiException
from typing_extensions import Literal

from mcli.api.engine.engine import run_kube_in_threadpool
from mcli.api.exceptions import KubernetesException
from mcli.api.kube.runs import get_runs
from mcli.api.kube.runs.api_delete_runs import _get_platform_runs, _validate_run_cache_equivalent
from mcli.api.model import Run
from mcli.utils.utils_kube import PlatformRun, delete_pod_tombstone, get_rank0_pod
from mcli.utils.utils_run_status import RunStatus


def _threaded_stop_runs(run_names: List[str], _runs: Optional[List[Run]] = None):
    """Threaded function for stopping a list of runs

    Note: The Kubernetes API requires the platform for each run. To get this, we need to
    call `get_runs`. A common way to get the list of run names is to have already called
    `get_runs`, so you can avoid a second call by passing the output of that call in as
    the `_runs` argument.

    Args:
        run_names: List of runs to stop
        _runs: Optional list of :type Run: objects used to avoid calling `get_runs` unnecessarily

    Returns:
        A list of :type Run: that were stopped

    Raises:
        KubernetesException: Raised if stopping any of the requested runs failed.
    """
    if not _runs:
        _runs = get_runs(run_names=run_names)
    else:
        _validate_run_cache_equivalent(run_names, _runs)

    run_dict: Dict[str, Run] = {r.name: r for r in _runs}
    platform_runs = _get_platform_runs(_runs)
    futures: Dict[Future[bool],
                  str] = {run_kube_in_threadpool(_get_and_stop_pods, pr): pr.name for pr in platform_runs
                         }  # type: ignore
    failed_runs: List[str] = []
    failed_status: Optional[HTTPStatus] = None
    for fs in as_completed(futures):
        run_name = futures[fs]
        run = run_dict[run_name]
        try:
            _ = fs.result()  # Succeeded if it didn't error
            run.status = RunStatus.STOPPED
        except (KubernetesException, ApiException) as e:
            failed_runs.append(run_name)
            # Keep the last failure status for the error raised below
            failed_status = e.status if isinstance(e, KubernetesException) else HTTPStatus(e.status)
    if failed_runs:
        raise KubernetesException(status=failed_status or HTTPStatus.INTERNAL_SERVER_ERROR,
                                  message=f'Failed to stop {len(failed_runs)} runs. Please try again. '
                                  f'The runs that failed to stop were:\n{failed_runs}')

    return list(run_dict.values())


def _get_and_stop_pods(platform_run: PlatformRun) -> bool:
    """Stop a single run by first getting the rank 0 pod and then deleting its tombstone
    file

    NOTE: Since the run will error if the rank 0 pod goes down, we only need to stop it
    explicitly.
    """

    namespace = platform_run.context.namespace
    assert namespace is not None, 'Invalid platform: namespace should never be None'

    try:
        # Get the rank 0 pod. If it doesn't exist, then return True since the run has likely failed
        rank0_pod = get_rank0_pod(platform_run.name, namespace)
    except RuntimeError:
        return True
    return delete_pod_tombstone(rank0_pod, namespace)


@overload
def stop_runs(run_names: List[str],
              timeout: Optional[float] = 10,
              future: Literal[False] = False,
              _runs: Optional[List[Run]] = None) -> List[Run]:
    ...


@overload
def stop_runs(run_names: List[str],
              timeout: Optional[float] = None,
              future: Literal[True] = True,
              _runs: Optional[List[Run]] = None) -> Future[List[Run]]:
    ...


def stop_runs(run_names: List[str],
              timeout: Optional[float] = 10,
              future: bool = False,
              _runs: Optional[List[Run]] = None) -> Union[List[Run], Future[List[Run]]]:
    """Stop a list of runs currently running in the MosaicML Cloud

    Args:
        run_names: A list of run names to stop
        timeout: Time, in seconds, in which the call should complete. If the call
            takes too long, a TimeoutError will be raised. If ``future`` is ``True``, this
            value will be ignored.
        future: Return the output as a :type concurrent.futures.Future:. If True, the
            call to `stop_runs` will return immediately and the request will be
            processed in the background. This takes precedence over the ``timeout``
            argument. To get the :type Run: output, use ``return_value.result()``
            with an optional ``timeout`` argument.
        _runs: Optional list of :type Run: objects used to avoid calling `get_runs`
            unnecessarily. See the note below

    Returns:
        A list of :type Run: for the runs that were stopped

    Raises:
        KubernetesException: Raised if stopping any of the requested runs failed. All
            successfully stopped runs will have the status `RunStatus.STOPPED`. You can
            freely retry any stopped and unstopped runs if this error is raised due to a
            connection issue.

    Note:
    The Kubernetes API requires the platform for each run. To get this, we need to
    call `get_runs`. A common way to get the list of run names is to have already called
    `get_runs`, so you can avoid a second call by passing the output of that call in as
    the `_runs` argument.
    """

    response: Future[List[Run]] = run_kube_in_threadpool(_threaded_stop_runs, run_names, _runs)  # type: ignore

    if not future:
        return response.result(timeout=timeout)
    else:
        return response
