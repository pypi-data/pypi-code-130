"""Balabit SCB driver."""
from typing import Any
import logging
import paramiko
from netmiko.linux import LinuxSSH
import socket

from typing import (
    Optional,
    Callable,
    Any,
    List,
    Dict,
    TypeVar,
    cast,
    Type,
    Sequence,
    Iterator,
    TextIO,
    Union,
    Tuple,
    Deque,
)
from netmiko.session_log import SessionLog


class SecretsFilter(logging.Filter):
    def __init__(self, no_log: Optional[Dict[Any, str]] = None) -> None:
        self.no_log = no_log

    def filter(self, record: logging.LogRecord) -> bool:
        """Removes secrets (no_log) from messages"""
        if self.no_log:
            for hidden_data in self.no_log.values():
                if isinstance(hidden_data, list):
                    for item in hidden_data:
                        record.msg = record.msg.replace(item, "********")
                else:
                    record.msg = record.msg.replace(hidden_data, "********")
        return True


import netmiko

netmiko.base_connection.SecretsFilter = SecretsFilter


class BalabitGWClient(paramiko.SSHClient):
    def _auth(
        self,
        username,
        password,
        pkey,
        key_filenames,
        allow_agent,
        look_for_keys,
        gss_auth,
        gss_kex,
        gss_deleg_creds,
        gss_host,
        passphrase,
    ):
        def balabit_gw_pw_handler(title, instructions, prompt_list):
            resp = []
            for pr in prompt_list:
                if str(pr[0]).strip() == "Gateway password:":
                    resp.append(password[0])
            return tuple(resp)

        self._transport.auth_interactive_dumb(username, balabit_gw_pw_handler)
        self._transport.auth_password(username, password[1])
        return


class BalabitSCB(LinuxSSH):
    pass


class BalabitSCBSSH(BalabitSCB):
    def _build_ssh_client(self):
        """Prepare for Paramiko SSH connection."""
        # Create instance of SSHClient object
        remote_conn_pre = BalabitGWClient()

        # Load host_keys for better SSH security
        if self.system_host_keys:
            remote_conn_pre.load_system_host_keys()
        if self.alt_host_keys and os.path.isfile(self.alt_key_file):
            remote_conn_pre.load_host_keys(self.alt_key_file)

        # Default is to automatically add untrusted hosts (make sure appropriate for your env)
        remote_conn_pre.set_missing_host_key_policy(self.key_policy)
        return remote_conn_pre

    def __init__(self, ip: str = "", host: str = "", username: str = "", password: Optional[str] = None, secret: str = "", port: Optional[int] = None, device_type: str = "", verbose: bool = False, global_delay_factor: float = 1, global_cmd_verify: Optional[bool] = None, use_keys: bool = False, key_file: Optional[str] = None, pkey: Optional[paramiko.PKey] = None, passphrase: Optional[str] = None, disabled_algorithms: Optional[Dict[str, Any]] = None, allow_agent: bool = False, ssh_strict: bool = False, system_host_keys: bool = False, alt_host_keys: bool = False, alt_key_file: str = "", ssh_config_file: Optional[str] = None, conn_timeout: int = 10, auth_timeout: Optional[int] = None, banner_timeout: int = 15, blocking_timeout: int = 20, timeout: int = 100, session_timeout: int = 60, read_timeout_override: Optional[float] = None, keepalive: int = 0, default_enter: Optional[str] = None, response_return: Optional[str] = None, serial_settings: Optional[Dict[str, Any]] = None, fast_cli: bool = True, _legacy_mode: bool = False, session_log: Optional[SessionLog] = None, session_log_record_writes: bool = False, session_log_file_mode: str = "write", allow_auto_change: bool = False, encoding: str = "utf-8", sock: Optional[socket.socket] = None, auto_connect: bool = True, delay_factor_compat: bool = False, target_device_type: str = "linux") -> None:
        self._target_device_type=target_device_type
        super().__init__(ip, host, username, password, secret, port, device_type, verbose, global_delay_factor, global_cmd_verify, use_keys, key_file, pkey, passphrase, disabled_algorithms, allow_agent, ssh_strict, system_host_keys, alt_host_keys, alt_key_file, ssh_config_file, conn_timeout, auth_timeout, banner_timeout, blocking_timeout, timeout, session_timeout, read_timeout_override, keepalive, default_enter, response_return, serial_settings, fast_cli, _legacy_mode, session_log, session_log_record_writes, session_log_file_mode, allow_auto_change, encoding, sock, auto_connect, delay_factor_compat)

    def _open(self) -> None:
        """Decouple connection creation from __init__ for mocking."""
        self._modify_connection_params()
        self.establish_connection(511, 511)
        self._try_session_preparation()
        if self._target_device_type:
            netmiko.redispatch(self,self._target_device_type)
            self.find_prompt()


import netmiko
from netmiko.ssh_dispatcher import CLASS_MAPPER

netmiko.platforms.append("balabit_scb")
CLASS_MAPPER["balabit_scb"] = BalabitSCBSSH
