from typing import Awaitable, Callable

from pyzeebe_fork.job.job import Job

ExceptionHandler = Callable[[Exception, Job], Awaitable]
