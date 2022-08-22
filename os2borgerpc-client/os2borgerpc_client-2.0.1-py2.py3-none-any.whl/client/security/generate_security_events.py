"""Generate security events for testing module."""
from datetime import datetime

AUTH_LOG = "/var/log/auth.log"
SYS_LOG = "/var/log/syslog"


def _generate_security_event(log_entry, log_file):
    """Helper-function for security events generators, handling writing to the log."""
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M")
    with open(log_file, "a") as log:
        log.write(f"{timestamp} {log_entry}")


def generate_sudo_event():
    """Add log entry matching a sudo event, produces a security event if enabled."""
    sudo_event_log_entry = (
        "bpc sudo: root : TTY=pts/0"
        " ; PWD=/home/user ; USER=root ; COMMAND=/usr/bin/ls\n"
    )
    _generate_security_event(sudo_event_log_entry, AUTH_LOG)


def generate_keyboard_event():
    """Add log entry matching a keyboard event, produces a security event if enabled."""
    keyboard_event_log_entry = (
        "bpc kernel: [ 9128.886664] input: Logitech Wireless Keyboard PID:4075 as "
        "/devices/pci0000:00/0000:00:14.0/usb1/1-2/1-2:1.1/0003:046D:C534.000A/"
        "0003:046D:4075.000B/input/input37"
    )
    _generate_security_event(keyboard_event_log_entry, SYS_LOG)


def generate_expired_event():
    """Add log entry matching an expired event, produces a security event if enabled."""
    expired_event_log_entry = (
        "bpc usermod[4507]: change user 'user' expiration from 'never' to '1970-01-02'"
    )
    _generate_security_event(expired_event_log_entry, SYS_LOG)
