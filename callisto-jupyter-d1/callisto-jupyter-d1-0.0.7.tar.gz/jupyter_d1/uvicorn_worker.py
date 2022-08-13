from uvicorn.config import LOGGING_CONFIG
from uvicorn.workers import UvicornWorker

LOGGING_CONFIG["formatters"]["default"][
    "fmt"
] = "%(asctime)s %(levelprefix)s - %(message)s"
LOGGING_CONFIG["formatters"]["access"][
    "fmt"
] = '%(asctime)s %(levelprefix)s - "%(request_line)s" %(status_code)s'


class D1UvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "loop": "asyncio",
        "http": "auto",
        "log_config": LOGGING_CONFIG,
    }
