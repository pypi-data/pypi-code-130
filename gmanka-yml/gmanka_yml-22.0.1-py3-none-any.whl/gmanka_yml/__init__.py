from pathlib import Path
import yaml


version = '22.0.1'


def to_str(
    data: any,
) -> str:
    return yaml.dump(
        data,
        Dumper = yaml.CDumper,
    )


def to_file(
    data: any,
    file_path: str | Path,
) -> None:
    with open(
        file_path,
        'w'
    ) as file:
        file.write(
            to_str(
                data,
            )
        )


def read_str(
    data: str,
) -> any:
    return yaml.load(
        data,
        Loader = yaml.CLoader,
    )


def read_file(
    file_path: str | Path
):
    with open(
        file_path,
        'r',
    ) as file:
        return read_str(
            file
        )
