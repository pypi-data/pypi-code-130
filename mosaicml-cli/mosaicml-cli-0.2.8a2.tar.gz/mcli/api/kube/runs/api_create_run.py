"""create_run SDK for Kubernetes"""

from __future__ import annotations

import datetime as dt
import uuid
from concurrent.futures import Future
from dataclasses import asdict
from typing import Optional, Union, overload

from typing_extensions import Literal

from mcli.api.engine.engine import run_kube_in_threadpool
from mcli.api.model.run import Run
from mcli.api.runs import create_run as mapi_create_run
from mcli.config import FeatureFlag, MCLIConfig
from mcli.models.mcli_integration import IntegrationType
from mcli.models.run_config import FinalRunConfig, RunConfig
from mcli.serverside.job.mcli_job import MCLIJob
from mcli.serverside.platforms.platform import PriorityLabel
from mcli.serverside.runners.runner import Runner
from mcli.utils.utils_run_status import RunStatus

__all__ = ['create_run']


def _submit_run(model: Run, mcli_job: MCLIJob, priority: Optional[str] = None) -> Run:
    """Submit a run and return the run model

    This is only used to provide the same "future" and "timeout" interface for the
    kubernetes calls as for the MAPI calls.

    Args:
        model: The run that will be returned
        mcli_job: The job that will be submitted
        priority: The priority that the job should be submitted at. Defaults to None.

    Returns:
        The run that was passed in
    """

    # Processes local integration before run starts
    for integration in mcli_job.integrations:
        if integration.integration_type == IntegrationType.local:
            integration.build_to_docker(mcli_job.image)

    Runner().submit(job=mcli_job, priority_class=priority)
    return model


@overload
def create_run(
    run: Union[RunConfig, FinalRunConfig],
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
    _priority: Optional[Union[PriorityLabel, str]] = None,
) -> Run:
    ...


@overload
def create_run(
    run: Union[RunConfig, FinalRunConfig],
    timeout: Optional[float] = None,
    future: Literal[True] = True,
    _priority: Optional[Union[PriorityLabel, str]] = None,
) -> Future[Run]:
    ...


def create_run(
    run: Union[RunConfig, FinalRunConfig],
    timeout: Optional[float] = 10,
    future: bool = False,
    _priority: Optional[Union[PriorityLabel, str]] = None,
):
    """Launch a run in the MosaicML Cloud

    The provided ``run`` must contain enough details to fully detail the run. If it does
    not, an error will be thrown.

    Args:
        run: A fully-configured run to launch. The run will be queued and persisted
            in the run database.
        timeout: Time, in seconds, in which the call should complete. If the run creation
            takes too long, a TimeoutError will be raised. If ``future`` is ``True``, this
            value will be ignored.
        future: Return the output as a :type concurrent.futures.Future:. If True, the
            call to `create_run` will return immediately and the request will be
            processed in the background. This takes precedence over the ``timeout``
            argument. To get the :type Run: output, use ``return_value.result()``
            with an optional ``timeout`` argument.
        _priority: An optional priority level at which the run should be created. Only
            effective for certain platforms. This argument is likely to be deprecated in
            the future.

    Raises:
        InstanceTypeUnavailable: Raised if an invalid compute instance is requsted

    Returns:
        A :type Run: that includes the launched run details and the run status
    """

    if isinstance(run, RunConfig):
        run = FinalRunConfig.finalize_config(run)

    if isinstance(_priority, PriorityLabel):
        _priority = _priority.value
        assert not isinstance(_priority, PriorityLabel)

    mcli_job = MCLIJob.from_final_run_config(run)

    # If requested, create run in MAPI and extract run_id and UUID
    conf = MCLIConfig.load_config(safe=True)
    if conf.feature_enabled(FeatureFlag.USE_FEATUREDB):
        model = mapi_create_run(run)
        # Ensure run has same unique name as is stored in MAPI
        mcli_job.run_id = model.name.split('-')[-1]
    else:
        mock_uuid = str(uuid.uuid4())
        model = Run(
            run_uid=mock_uuid,
            name=mcli_job.unique_name,
            status=RunStatus.PENDING,
            created_at=dt.datetime.now(),
            updated_at=dt.datetime.now(),
            config=run,
            job_config=asdict(mcli_job),
        )

    res = run_kube_in_threadpool(_submit_run, model, mcli_job, _priority)

    if not future:
        return res.result(timeout=timeout)
    else:
        return res
