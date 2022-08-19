import json


def read_jsonl(filepath):
    """Reads JSONL and outputs JSON

    Args:
        filepath (str): Filepath to JSONL file

    Returns:
        JSON: JSON file
    """
    data = [json.loads(l) for l in open(filepath)]
    return data


def write_jsonl(injson, filepath):
    """Writes JSONL

    Args:
        injson (JSON): JSON file
        filepath (str): Output filepath (include file name and extension)
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in injson:
            f.write(json.dumps(item) + "\n")


def read_json(filepath):
    """Read JSON file

    Args:
        filepath (str): Filepath to JSON file

    Returns:
        JSON: JSON file
    """
    with open(filepath) as f:
        return json.load(f)


def write_json(injson, filepath):
    """Writes JSON

    Args:
        injson (JSON): JSON file
        filepath (str): Output filepath (include file name and extension)
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(injson, f, ensure_ascii=False)
