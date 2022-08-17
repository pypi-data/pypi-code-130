import json


def load_json(file_name):
    with open(file_name, encoding="utf-8", mode="r") as file:
        return json.load(file)


def save_json(file_name, data, indent=4):
    with open(file_name, encoding="utf-8", mode="w") as file:
        json.dump(data, file, indent=indent)
