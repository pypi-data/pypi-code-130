def write_error_to_log(action, path):
    """
    This method writes an error to the log.
    Arguments:
        action: The action that was executed.
        path: The path of the element that was executed.
    """
    return print(f'Error: {action} on {path}')