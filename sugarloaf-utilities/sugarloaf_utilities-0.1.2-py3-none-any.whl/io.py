from asyncio import (
    TimeoutError,
    create_subprocess_shell,
    run as async_run,
    wait_for,
)
from asyncio.subprocess import PIPE
from dataclasses import dataclass
from typing import List


@dataclass
class SubprocessResult:
    stdout: str
    stderr: str
    returncode: int


class EchoSubprocess:
    """
    Echos a subprocess in realtime and returns the result after its complete. This can
    be thought of as combining Popen's capture_output and a streaming output to the shared
    parent process's stdout. Also allows for stdin input during execution.

    """
    def __init__(self, command: List[str]):
        self.command = " ".join(command)

    def run(self):
        """
        Spawn the subprocess and return the execution log.
        """
        return async_run(self.echo_subprocess_async())

    async def echo_subprocess_async(self, wait_interval=5):
        p = await create_subprocess_shell(self.command, stdout=PIPE, stderr=PIPE)

        logs = {
            "stdout": "",
            "stderr": "",
        }

        while True:
            for log_key, stream in [("stdout", p.stdout), ("stderr", p.stderr)]:
                # read data byte-by-byte to consume all pending characters in the buffer
                # requesting a full newline (via readline) will timeout without returning
                # if a newline hasn't yet been echoed
                while True:
                    # Get up to the buffer size and immediately return
                    new_content = await stream.read(1024)

                    print(new_content.decode(errors="ignore"), end="", flush=True)
                    logs[log_key] += new_content.decode(errors="ignore")

                    if not new_content:
                        break

            if p.returncode is not None:
                break

        return SubprocessResult(
            stdout="".join(logs["stdout"]),
            stderr="".join(logs["stderr"]),
            returncode=p.returncode
        )
