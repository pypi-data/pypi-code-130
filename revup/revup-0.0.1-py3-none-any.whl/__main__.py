# aclint: py3
from revup.types import RevupUsageException, RevupConflictException
from revup.revup import main

import asyncio
import logging
import sys

try:
    # Exit code of 1 is reserved for exception-based exits
    sys.exit(asyncio.run(main()))
except RevupUsageException as e:
    logging.error(str(e))
    sys.exit(2)
except RevupConflictException as e:
    logging.error(str(e))
    sys.exit(3)
