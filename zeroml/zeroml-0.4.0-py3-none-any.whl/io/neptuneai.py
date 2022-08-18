from pathlib import Path
from typing import Union

import neptune.new as neptune


def download_from_neptune(
    project_name: str, experiment_name: str, neptune_file: str, out_path_or_file: Union[str, Path]
):
    run = neptune.init(project_name, run=experiment_name)
    run[neptune_file].download(str(out_path_or_file))
