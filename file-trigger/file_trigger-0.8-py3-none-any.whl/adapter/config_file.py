import os.path

try:
    import tomllib
except ImportError:
    import tomli as tomllib
from typing import Any, Optional, Iterable, List, Dict

from ..model.config import Config, HandlerConfig, Command
from ..util.watchdog import event_type_from_string
from ..util import dict_
from ..util.dataclasses_ import nonoptional_nonlist_fields, nonoptional_fields
from ..util.bool_ import strict_bool

TOP_LEVEL_KEY = "file-trigger"
LOGGING_KEY = "logging"


def parse_file(file: str) -> Config:
    raw: Dict[str, Any] = {}
    with open(file, "rb") as f:
        raw = tomllib.load(f)

    assert_config_keys(raw, [TOP_LEVEL_KEY], [LOGGING_KEY])

    logging_data = raw[LOGGING_KEY]
    if not isinstance(logging_data, dict):
        raise ValueError(f"Unknown logging configuration: {logging_data}")

    data = raw[TOP_LEVEL_KEY]
    if not isinstance(data, dict):
        raise ValueError(f"Unknown top-level configuration: {data}")

    assert_config_keys(
        raw,
        *[
            [TOP_LEVEL_KEY, k]
            for k in nonoptional_nonlist_fields(Config)
            if not k == "logging"
        ],
    )

    empty_root_dir_aliases: List[str] = []
    patterns = data.get("patterns", None)
    ignore_patterns = data.get("ignore_patterns", None)
    root_dir_aliases = data.get("root_dir_aliases", empty_root_dir_aliases)
    notify_logger = data.get("notify_logger", None)

    return Config(
        root_dir=parse_root_dir(str(data["root_dir"])),
        recursive=strict_bool("recursive", data["recursive"]),
        patterns=None if patterns is None else list(str(p) for p in patterns),
        ignore_patterns=None
        if ignore_patterns is None
        else list(str(p) for p in ignore_patterns),
        ignore_directories=strict_bool(
            "ignore_directories", data["ignore_directories"]
        ),
        root_dir_aliases=list(str(a) for a in root_dir_aliases),
        notify_logger=None if notify_logger is None else str(notify_logger),
        handlers=parse_handlers(raw, [TOP_LEVEL_KEY, "handler"]),
        logging=logging_data,
    )


def parse_root_dir(raw: str) -> str:
    return os.path.abspath(raw)


def parse_handlers(data: Dict[str, Any], keys: List[str]) -> List[HandlerConfig]:
    handlers_data = dict_.path(keys, data)
    if not isinstance(handlers_data, dict):
        raise ValueError(f"Unknown handlers configuration: {handlers_data}")
    return [parse_handler(data, keys, k) for k in handlers_data]


def parse_handler(data: Dict[str, Any], keys: List[str], name: str) -> HandlerConfig:
    assert_config_keys(
        data,
        *[
            keys + [name, field]
            for field in nonoptional_nonlist_fields(HandlerConfig)
            if not field == "name"
        ],
    )
    handler_data = dict_.path(keys + [name], data)
    if not isinstance(handler_data, dict):
        raise ValueError(f"Unknown handler configuration {name}: {handler_data}")

    events: Optional[List[str]] = handler_data.get("events", None)
    command_names: List[str] = handler_data.get("commands", [])

    return HandlerConfig(
        name=name,
        template=str(handler_data["template"]),
        events=(
            None
            if events is None
            else set(event_type_from_string(str(x)) for x in events)
        ),
        commands=parse_commands(data, [TOP_LEVEL_KEY], command_names),
    )


def parse_commands(
    data: Dict[str, Any], keys: List[str], command_names: List[str]
) -> List[Command]:
    commands_data = dict_.path(keys + ["command"], data)
    if not isinstance(commands_data, dict):
        raise ValueError(f"Unknown commands configuration: {commands_data}")
    return [parse_command(data, keys, k) for k in command_names]


def parse_command(data: Dict[str, Any], keys: List[str], name: str) -> Command:
    assert_config_keys(
        data,
        *[
            keys + ["command", name, field]
            for field in nonoptional_fields(Command)
            if not field == "name"
        ],
    )
    command_data = dict_.path(keys + ["command", name], data)
    if not isinstance(command_data, dict):
        raise ValueError(f"Unknown command configuration {name}: {command_data}")
    cwd = command_data.get("cwd", None)
    shell = command_data.get("shell", None)
    timeout = command_data.get("timeout", None)
    error_rc = command_data.get("error_rc", None)
    warning_rc = command_data.get("warning_rc", None)
    notify = command_data.get("notify", None)
    params = {
        "name": name,
        "command": list(str(x) for x in command_data["command"]),
        "cwd": None if cwd is None else str(cwd),
    }
    if shell is not None:
        params["shell"] = strict_bool("shell", shell)
    if timeout is not None:
        params["timeout"] = float(timeout)
    if error_rc is not None:
        params["error_rc"] = int(error_rc)
    if warning_rc is not None:
        params["warning_rc"] = int(warning_rc)
    if notify is not None:
        params["notify"] = dict_.strict_dict("notify", notify)

    return Command(**params)  # type: ignore


def assert_config_keys(d: Dict[str, Any], *paths: Iterable[str]) -> None:
    missings = []
    for path in paths:
        try:
            v = dict_.path(path, d)
            if v is None:
                missings.append(path)
        except KeyError:
            missings.append(path)
    if len(missings) == 1:
        msg = ".".join(missings[0])
        raise ValueError(f"Missing configuration: {msg}")
    if len(missings) > 1:
        msg = "\n  ".join([".".join(m) for m in missings])
        raise ValueError(f"Missing configurations:\n  {msg}")
