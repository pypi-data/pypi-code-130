"""Implements the API get_run_logs for Kubernetes"""
from __future__ import annotations

import re
from datetime import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING, Generator, NamedTuple, Optional, Union

import arrow

from mcli.api.exceptions import KubernetesException
from mcli.models.mcli_platform import MCLIPlatform
from mcli.utils.utils_kube import get_pod_rank, list_run_pods, read_pod_logs, stream_pod_logs
from mcli.utils.utils_run_status import RunStatus

if TYPE_CHECKING:
    from mcli.api.kube.runs import Run

# Sometimes Kubernetes garbage collects the logs and you see this line instead
ERROR_LINE = r'unable to retrieve container logs for containerd.*'


class LogRecord(NamedTuple):
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
    def splitlines(cls, text: str) -> Generator[LogRecord, None, None]:
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
                    yield LogRecord.from_line(prev_line.rstrip('\n'))
                prev_line = line
        if prev_line:
            yield LogRecord.from_line(prev_line.rstrip('\n'))

    @classmethod
    def from_line(cls, line: str) -> LogRecord:
        """Parse a line of logs to extract the timestamp and remaining text

        Args:
            line (str): A line of logs

        Raises:
            KubernetesException (HTTPStatus.INTERNAL_SERVER_ERROR): Raised if the log line
                could not be parsed

        Returns:
            LogRecord: the parsed record for the log line
        """
        if re.match(ERROR_LINE, line):
            raise KubernetesException(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                message='Logs seem to have been corrupted. Unable to retrieve logs for this run',
            )
        ts, text = line.split(' ', 1)
        try:
            timestamp = arrow.get(ts).datetime
        except arrow.parser.ParserError as e:
            raise KubernetesException(
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f'Unable to parse log line because there was no timestamp:\n\n{line}') from e
        return LogRecord(text, timestamp)


def _threaded_get_run_logs(run: Union[str, Run],
                           rank: Optional[int] = None,
                           follow: bool = False) -> Generator[LogRecord, None, None]:
    """Threaded function to provide a generator of ``LogRecord``s for the given run

    Args:
        run (Union[str, Run]): The run to get logs for. If a name is provided, the
            remaining required run details will be queried with ``get_runs([run])``.
        rank (Optional[int]): Node rank of a run to get logs for. Defaults to the lowest
            available rank. This will usually be rank 0 unless something has gone wrong.
        follow (bool): Whether to follow ongoing logs for an active run. Defaults to
            False. If ``follow`` is ``False``, only logs up to the time the function
            is called will be returned.

    Raises:
        KubernetesException (HTTPStatus.NOT_FOUND): Raised if the requested run does not exist
        KubernetesException (HTTPStatus.BAD_REQUEST): Raised if the run is not yet running,
            or if the run does not have a node of the requested rank.

    Yields:
        LogRecord: A ``LogRecord`` for every line of the run's logs
    """
    if isinstance(run, str):
        # Get run info if a name was provided
        # pylint: disable-next=import-outside-toplevel
        from mcli.api.kube.runs import get_runs

        runs = get_runs([run])
        if not runs:
            # Run doesn't exist -> Raise 404
            raise KubernetesException(status=HTTPStatus.NOT_FOUND, message=f'Could not find run: {run}')
        run = runs[0]

    if run.status.before(RunStatus.RUNNING):
        # Run hasn't started yet, so error
        raise KubernetesException(status=HTTPStatus.BAD_REQUEST,
                                  message=f'Run {run.name} hasn\'t started running yet. '
                                  f'It currently has a status of: {run.status.value.lower()}. '
                                  'Please wait and try again. '
                                  'You can wait using:\n\n'
                                  f'wait_for_run_status("{run.name}", status=RunStatus.RUNNING)')

    with MCLIPlatform.use(run.config.platform) as platform:
        # Get all possible pods
        pods = list_run_pods(run.name, platform.namespace)

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

        pod_name = pod.metadata.name
        if follow:
            for line in stream_pod_logs(pod_name, platform.namespace, timestamps=True):
                yield LogRecord.from_line(line)
        else:
            for record in LogRecord.splitlines(read_pod_logs(pod_name, platform.namespace, timestamps=True)):
                yield record


def get_run_logs(run: Union[str, Run],
                 rank: Optional[int] = None,
                 follow: bool = False) -> Generator[LogRecord, None, None]:
    """Get the logs for an active or completed run in the MosaicML Cloud

    Args:
        run (Union[str, Run]): The run to get logs for. If a name is provided, the
            remaining required run details will be queried with ``get_runs([run])``.
        rank (Optional[int]): Node rank of a run to get logs for. Defaults to the lowest
            available rank. This will usually be rank 0 unless something has gone wrong.
        follow (bool): Whether to follow ongoing logs for an active run. Defaults to
            False. If ``follow`` is ``False``, only logs up to the time the function
            is called will be returned.

    Raises:
        KubernetesException (HTTPStatus.NOT_FOUND): Raised if the requested run does not exist
        KubernetesException (HTTPStatus.BAD_REQUEST): Raised if the run is not yet running,
            or if the run does not have a node of the requested rank.

    Yields:
        LogRecord: A ``LogRecord`` for every line of the run's logs
    """

    yield from _threaded_get_run_logs(run, rank=rank, follow=follow)
