from pathlib import Path
from typing import Dict, List, Union
from datamodel_code_generator import InputFileType, generate
import pandas as pd


def generated_database_model(
    database: Dict[str, pd.DataFrame],
    model_path: Union[Path, str] = "model.py",
):
    database_json = "{"
    for df_name, df in database.items():
        database_json = (
            database_json + f'"{df_name}":' + df.iloc[0].to_json() + ","
        )
    database_json = database_json[:-1] + "}"

    generate(
        database_json,
        input_file_type=InputFileType.Json,
        output=Path(model_path),
    )
