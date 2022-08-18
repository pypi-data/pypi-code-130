"""Implementation of the delete_runs API for Kubernetes"""
from __future__ import annotations

import logging
from concurrent.futures import Future
from concurrent.futures import TimeoutError as FutureTimeoutError
from concurrent.futures import wait
from http import HTTPStatus
from typing import Dict, List, Optional, Set, Union, cast, overload

from typing_extensions import Literal

from mcli.api.engine.engine import run_kube_in_threadpool
from mcli.api.exceptions import KubernetesException
from mcli.api.model.run import Run
from mcli.api.runs import delete_runs as mapi_delete_runs
from mcli.config import FeatureFlag, MCLIConfig
from mcli.models.mcli_platform import MCLIPlatform
from mcli.utils.utils_kube import KubeContext, PlatformRun
from mcli.utils.utils_kube import delete_runs as _util_delete_runs

__all__ = ['delete_runs']

logger = logging.getLogger(__name__)


def _threaded_delete_runs(runs: Union[List[str], List[Run]]) -> List[Run]:
    """Threaded function for deleting a list of runs

    Args:
        runs: List of runs to delete

    Returns:
        A list of :type Run: that were deleted
    """
    if not runs:
        return []

    if not all(isinstance(r, Run) for r in runs):
        # pylint: disable-next=import-outside-toplevel
        from mcli.api.kube.runs import get_runs
        runs = get_runs(runs=[r.name if isinstance(r, Run) else r for r in runs])
    runs = cast(List[Run], runs)

    platform_runs = _get_platform_runs(runs)
    success = _util_delete_runs(platform_runs)
    if not success:
        # TODO: Figure out what error to throw here
        raise KubernetesException(status=HTTPStatus.INTERNAL_SERVER_ERROR, message='Delete failed!')
    return runs


def _get_platform_runs(runs: List[Run]) -> List[PlatformRun]:
    """Get a list of PlatformRun tuples so we know where to look for each run
    """

    platform_runs: List[PlatformRun] = []
    platform_context_map: Dict[str, KubeContext] = {}
    unknown_platforms: Set[str] = set()
    for run in runs:
        platform = run.config.platform
        if platform not in platform_context_map:
            try:
                context = MCLIPlatform.get_by_name(platform).to_kube_context()
            except KeyError:
                unknown_platforms.add(platform)
                continue
            platform_context_map[platform] = context
        platform_runs.append(PlatformRun(run.name, platform_context_map[platform]))

    if unknown_platforms:
        names = ', '.join(sorted(list(unknown_platforms)))
        message = f'Some runs could not be deleted because the following platforms are not configured locally: {names}'
        if platform_runs:
            # Some runs can be deleted, so just throw a warning
            logger.warning(message)
        else:
            # No runs can be deleted. This is likely a full failure, so let's throw an error
            raise RuntimeError(message)
    return platform_runs


@overload
def delete_runs(
    runs: Union[List[str], List[Run]],
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> List[Run]:
    ...


@overload
def delete_runs(
    runs: Union[List[str], List[Run]],
    timeout: Optional[float] = None,
    future: Literal[True] = True,
) -> Future[List[Run]]:
    ...


def delete_runs(
    runs: Union[List[str], List[Run]],
    timeout: Optional[float] = 10,
    future: bool = False,
) -> Union[List[Run], Future[List[Run]]]:
    """Delete a list of runs in the MosaicML Cloud

    Any runs that are currently running will first be stopped.

    Args:
        runs: A list of runs or run names to delete. Using ``Run`` objects is most
            efficient. See the note below.
        timeout: Time, in seconds, in which the call should complete. If the call
            takes too long, a TimeoutError will be raised. If ``future`` is ``True``, this
            value will be ignored.
        future: Return the output as a :type concurrent.futures.Future:. If True, the
            call to `delete_runs` will return immediately and the request will be
            processed in the background. This takes precedence over the ``timeout``
            argument. To get the :type Run: output, use ``return_value.result()``
            with an optional ``timeout`` argument.

    Returns:
        A list of :type Run: for the runs that were deleted

    Note:
    The Kubernetes API requires the platform for each run. If you provide ``runs`` as a
    list of names, we will get this by calling `get_runs`. Since a common way to get the
    list of runs is to have already called `get_runs`, you can avoid a second call by
    passing the output of that call in directly.
    """

    conf = MCLIConfig.load_config(safe=True)
    mapi_future: Optional[Future[List[Run]]] = None
    if conf.feature_enabled(FeatureFlag.USE_FEATUREDB):
        mapi_future = mapi_delete_runs(runs=runs, future=True)

    kube_future = run_kube_in_threadpool(_threaded_delete_runs, runs=runs)

    if not future:
        if mapi_future is not None:
            _, not_done = wait([mapi_future, kube_future], timeout=timeout)
            if not_done:
                failed = ['MAPI' if f == mapi_future else 'Kubernetes' for f in not_done]
                raise FutureTimeoutError(f'Delete call timed out to: {" and ".join(failed)}')
        return kube_future.result(timeout=timeout)
    else:
        return kube_future
