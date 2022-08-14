from pathlib import Path
from typing import List

import joblib
import pandas as pd

from scoringmodel import __version__ as _version
from scoringmodel.config.core import DATASET_DIR, TRAINED_MODEL_DIR, config


def load_dataset(file_name: str) -> pd.DataFrame:
    rawdata = pd.read_excel(Path(f"{DATASET_DIR}/{file_name}"), 
                            index_col=0, header=1
                            )

    # rename variables with spaces, pay_0 to pay_1, and to lowercases
    transformed = rawdata.rename(columns=config.model_config.variables_to_rename)
    transformed.columns = [col.lower() for col in transformed.columns] 

    return transformed

def remove_old_model(*, files_to_keep: List[str]) -> None:
    """
    """
    do_not_delete = files_to_keep + ["__init__.py"]
    for model_file in TRAINED_MODEL_DIR.iterdir():
        if model_file.name not in do_not_delete:
            model_file.unlink()

    return None

def save_model(*, model_to_persist) -> None:
    """
    """
    # Prepare versioned save file name
    save_file_name = f"{config.app_config.model_save_file}{_version}.pkl"
    save_path = TRAINED_MODEL_DIR / save_file_name

    remove_old_model(files_to_keep=[save_file_name])
    joblib.dump(model_to_persist, save_path)

    return None


def load_model(*, file_name: str):
    """Load a persisted pipeline."""

    file_path = TRAINED_MODEL_DIR / file_name
    trained_model = joblib.load(filename=file_path)
    return trained_model
