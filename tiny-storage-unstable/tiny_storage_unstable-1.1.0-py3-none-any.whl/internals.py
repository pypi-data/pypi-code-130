def pull(data, path, value):
    if len(path) == 0:
        return False, data

    assert isinstance(data, dict), "you can pull only from a dict"

    if callable(value):
        value = value()

    if path[0] in data:
        return pull(data.get(path[0]), path[1:], value)

    return False, value


def push(data, path, value):
    assert isinstance(data, dict), "you can push value only into dict"

    if callable(value):
        value = value()

    if len(path) == 1:
        was_modified = path[0] not in data or data[path[0]] != value

        data[path[0]] = value
        return was_modified, value

    if path[0] in data:
        return push(data[path[0]], path[1:], value)

    data[path[0]] = {}
    return push(data[path[0]], path[1:], value)


def put(data, path, value):
    if len(path) == 0:
        return False, data

    assert isinstance(data, dict), "you can put value only onto dict"

    if path[0] in data:
        return put(data[path[0]], path[1:], value)

    if len(path) == 1:
        if callable(value):
            value = value()

        data[path[0]] = value
        return True, value

    data[path[0]] = {}
    return put(data[path[0]], path[1:], value)
