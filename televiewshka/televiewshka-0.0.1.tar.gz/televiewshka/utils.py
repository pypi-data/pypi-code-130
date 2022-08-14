from .views import AbstractBaseView


def get_trimmed_command(command: str) -> str:
    trimmed_command = command 
    if command.startswith("/"):
        trimmed_command = command[1:]
        if not len(trimmed_command):
            raise ValueError("Empty command")
    return trimmed_command
