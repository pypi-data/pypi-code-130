"""Implements the API get_run_logs for Kubernetes"""
from __future__ import annotations

import re
from concurrent.futures import Future
from datetime import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING, Generator, NamedTuple, Optional, Union, overload

import arrow
from typing_extensions import Literal

from mcli.api.engine.engine import run_in_threadpool
from mcli.api.exceptions import KubernetesException
from mcli.models.mcli_platform import MCLIPlatform
from mcli.utils.utils_kube import get_pod_rank, list_run_pods, read_pod_logs, stream_pod_logs
from mcli.utils.utils_run_status import RunStatus

if TYPE_CHECKING:
    from mcli.api.kube.runs import Run

# Sometimes Kubernetes garbage collects the logs and you see this line instead
ERROR_LINE = r'unable to retrieve container logs for containerd.*'
FAILED_WATCH_LINE = r'failed to watch file "/var/lib/docker/containers/.*'


class LogLine(NamedTuple):
    """A single line of a run's logs

    To print a record, use:
    ```python
    # Print the line with timestamp
    print(str(record))

    # Print the line without timestamp
    print(record.text)
    ```

    Attributes:
        text: The text of the line
        timestamp: The timestamp at which the line was written
    """
    text: str
    timestamp: datetime

    def __str__(self) -> str:
        return f'{self.timestamp.isoformat()} {self.text}'

    def __repr__(self) -> str:
        return f'LogRecord({repr(self.text)}, {repr(self.timestamp)})'

    @classmethod
    def splitlines(cls, text: str) -> Generator[LogLine, None, None]:
        """Split logs on lines that start with a timestamp

        Args:
            text: Full Kubernetes log

        Yields:
            LogRecord: A parsed record for each log line
        """
        prev_line: str = ''
        for line in text.splitlines(keepends=True):
            # Check if line startswith a timestamp
            try:
                _ = arrow.get(line.split(' ', 1)[0])
            except arrow.parser.ParserError:
                # No timestamp
                prev_line += line
            else:
                # Line starts with a timestamp, so yield prev_line
                if prev_line:
                    yield LogLine.from_line(prev_line.rstrip('\n'))
                prev_line = line
        if prev_line:
            yield LogLine.from_line(prev_line.rstrip('\n'))

    @classmethod
    def validate_line(cls, text: str) -> Literal[True]:
        """Validate that log text is not corrupted

        Args:
            text: A run's log text

        Raises:
            KubernetesException (HTTPStatus.INTERNAL_SERVER_ERROR): Raised if the log
                text is corrupted

        Returns:
            True if an exception was not raised
        """
        if re.match(ERROR_LINE, text) or re.match(FAILED_WATCH_LINE, text):
            raise KubernetesException(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                message='Logs seem to have been corrupted. Unable to retrieve logs for this run',
            )
        return True

    @classmethod
    def from_line(cls, line: str) -> LogLine:
        """Parse a line of logs to extract the timestamp and remaining text

        Args:
            line (str): A line of logs

        Raises:
            KubernetesException (HTTPStatus.INTERNAL_SERVER_ERROR): Raised if the log line
                could not be parsed

        Returns:
            LogRecord: the parsed record for the log line
        """
        cls.validate_line(line)
        ts, text = line.split(' ', 1)
        try:
            timestamp = arrow.get(ts).datetime
        except arrow.parser.ParserError as e:
            raise KubernetesException(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f'Unable to parse log line because there was no timestamp:\n\n{line}') from e
        return LogLine(text, timestamp)


def _threaded_get_run_logs(run: Union[str, Run], rank: Optional[int] = None, timestamps: bool = False) -> str:
    """Threaded function to provide a the current logs for the given run
    """
    if isinstance(run, str):
        # Get run info if a name was provided
        run = _get_run(run)

    with MCLIPlatform.use(run.config.platform) as platform:
        pod_name = _get_run_pod_name(run, namespace=platform.namespace, rank=rank)
        logs = read_pod_logs(pod_name, platform.namespace, timestamps=timestamps)

        # Validate that the logs weren't corrupted or lost
        LogLine.validate_line(logs)

        return logs


def _threaded_follow_run_logs(run: Union[str, Run],
                              rank: Optional[int] = None,
                              timestamps: bool = False) -> Generator[str, None, None]:
    """Threaded function to provide a generator of lines for the given run
    """
    if isinstance(run, str):
        # Get run info if a name was provided
        run = _get_run(run)

    def _wrapped_log_generator(name, namespace, timestamps) -> Generator[str, None, None]:
        """Wrap the log line generator. This lets the rest of _threaded_follow_run_logs
        execute when called, otherwise _get_run call would also wait until the first line
        was requested
        """
        for line in stream_pod_logs(name, namespace, timestamps=timestamps):
            # Validate that the line wasn't corrupted or lost
            LogLine.validate_line(line)
            yield line

    with MCLIPlatform.use(run.config.platform) as platform:
        pod_name = _get_run_pod_name(run, namespace=platform.namespace, rank=rank)
        return _wrapped_log_generator(pod_name, platform.namespace, timestamps)


def _get_run(run_name: str) -> Run:
    """Get a run from a run name
    """

    # pylint: disable-next=import-outside-toplevel
    from mcli.api.kube.runs import get_runs

    runs = get_runs([run_name])
    if not runs:
        # Run doesn't exist -> Raise 404
        raise KubernetesException(status=HTTPStatus.NOT_FOUND, message=f'Could not find run: {run_name}')
    return runs[0]


def _get_run_pod_name(run: Run, namespace: str, rank: Optional[int] = None) -> str:
    """Get the appropriate pod from a run
    """
    if run.status.before(RunStatus.RUNNING):
        # Run hasn't started yet, so error
        raise KubernetesException(status=HTTPStatus.BAD_REQUEST,
                                  message=f'Run {run.name} hasn\'t started running yet. '
                                  f'It currently has a status of: {str(run.status.value).lower()}. '
                                  'Please wait and try again. '
                                  'You can wait using:\n\n'
                                  f'wait_for_run_status("{run.name}", status=RunStatus.RUNNING)')

    # Get all possible pods
    pods = list_run_pods(run.name, namespace)

    # Get the requested rank or error
    rank_dict = {get_pod_rank(pod): pod for pod in pods}
    if rank is None:
        rank = sorted(list(rank_dict))[0]
        pod = rank_dict[rank]
    elif rank in rank_dict:
        pod = rank_dict[rank]
    else:
        raise KubernetesException(status=HTTPStatus.BAD_REQUEST,
                                  message=f'Could not find a node with rank {rank} for run {run.name}. '
                                  f'Valid ranks are: {", ".join(str(i) for i in sorted(list(rank_dict)))}')

    return pod.metadata.name


@overload
def get_run_logs(
    run: Union[str, Run],
    rank: Optional[int] = None,
    timestamps: bool = False,
    timeout: Optional[float] = None,
    future: Literal[True] = True,
) -> Future[str]:
    ...


@overload
def get_run_logs(
    run: Union[str, Run],
    rank: Optional[int] = None,
    timestamps: bool = False,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> str:
    ...


def get_run_logs(
    run: Union[str, Run],
    rank: Optional[int] = None,
    timestamps: bool = False,
    timeout: Optional[float] = 10,
    future: bool = False,
) -> Union[str, Future[str]]:
    """Get the current logs for an active or completed run in the MosaicML Cloud

    This returns the full logs as a ``str``, as they exist at the time the request is
    made. If you want to follow the logs for an active run line-by-line, use
    ``follow_run_logs``.

    Args:
        run (Union[str, Run]): The run to get logs for. If a name is provided, the
            remaining required run details will be queried with ``get_runs([run])``.
        rank (Optional[int]): Node rank of a run to get logs for. Defaults to the lowest
            available rank. This will usually be rank 0 unless something has gone wrong.
        timestamps (bool): If ``True``, each log line will also contain the timestamp at
            which it was emitted. If you wish to parse out a line's timestamp and text,
            you can use ``LogLine.from_line``.
        timeout: Time, in seconds, in which the call should complete. If the call
            takes too long, a TimeoutError will be raised. If ``future`` is ``True``, this
            value will be ignored.
        future: Return the output as a :type concurrent.futures.Future:. If True, the
            call to `get_run_logs` will return immediately and the request will be
            processed in the background. This takes precedence over the ``timeout``
            argument. To get the logs, then use ``return_value.result()``
            with an optional ``timeout`` argument.

    Raises:
        KubernetesException (HTTPStatus.NOT_FOUND): Raised if the requested run does not exist
        KubernetesException (HTTPStatus.BAD_REQUEST): Raised if the run is not yet running,
            or if the run does not have a node of the requested rank.

    Returns:
        If timeout is provided:
            str: The full log text for a run at the time of the request
        If using futures:
            Future[str]: A ``concurrent.futures.Future`` for the run's log text
    """

    future_logs = run_in_threadpool(KubernetesException.wrap(_threaded_get_run_logs),
                                    run,
                                    rank=rank,
                                    timestamps=timestamps)

    if not future:
        return future_logs.result(timeout=timeout)
    else:
        return future_logs


@overload
def follow_run_logs(
    run: Union[str, Run],
    rank: Optional[int] = None,
    timestamps: bool = False,
    timeout: Optional[float] = 10,
    future: Literal[False] = False,
) -> Generator[str, None, None]:
    ...


@overload
def follow_run_logs(
    run: Union[str, Run],
    rank: Optional[int] = None,
    timestamps: bool = False,
    timeout: Optional[float] = None,
    future: Literal[True] = True,
) -> Future[Generator[str, None, None]]:
    ...


def follow_run_logs(
    run: Union[str, Run],
    rank: Optional[int] = None,
    timestamps: bool = False,
    timeout: Optional[float] = 10,
    future: bool = False,
) -> Union[Generator[str, None, None], Future[Generator[str, None, None]]]:
    """Follow the logs for an active or completed run in the MosaicML Cloud

    This returns a generator of individual log lines, line-by-line, and will wait until
    new lines are produced if the run is still active. If you are only looking for the
    logs up until the time of the request, consider using ``get_run_logs`` instead.

    Args:
        run (Union[str, Run]): The run to follow logs for. If a name is provided, the
            remaining required run details will be queried with ``get_runs([run])``.
        rank (Optional[int]): Node rank of a run to follow logs for. Defaults to the lowest
            available rank. This will usually be rank 0 unless something has gone wrong.
        timestamps (bool): If ``True``, each log line will also contain the timestamp at
            which it was emitted. If you wish to parse out a line's timestamp and text,
            you can use ``LogLine.from_line``.
        timeout: Time, in seconds, in which the initial connection call should complete.
            If the call takes too long, a TimeoutError will be raised. If ``future`` is
            ``True``, this value will be ignored. Default 10.
        future: Return the generator as a :type concurrent.futures.Future:. If True, the
            call to `follow_run_logs` will return immediately and the request will be
            processed in the background. This takes precedence over the ``timeout``
            argument. To get the logs, then use ``return_value.result()``
            with an optional ``timeout`` argument.

    Raises:
        KubernetesException (HTTPStatus.NOT_FOUND): Raised if the requested run does not exist
        KubernetesException (HTTPStatus.BAD_REQUEST): Raised if the run is not yet running,
            or if the run does not have a node of the requested rank.

    Returns:
        If timeout is provided:
            Generator[str]: A line-by-line generator of the logs for a run
        If using futures:
            Future[Generator[str]]: A ``concurrent.futures.Future`` of a line-by-line
                generator of the logs for a run
    """
    # A Future request for a log stream. The stream itself will generate Futures for individual log lines
    log_stream_request = run_in_threadpool(
        _threaded_follow_run_logs,
        run,
        rank=rank,
        timestamps=timestamps,
    )
    if not future:
        return log_stream_request.result(timeout=timeout)
    else:
        return log_stream_request
