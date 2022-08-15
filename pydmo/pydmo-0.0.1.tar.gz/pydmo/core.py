from pathlib import Path
from typing import Dict, Union

import pandas as pd
from datamodel_code_generator import InputFileType, generate


def generate_database_model(
    database: Dict[str, pd.DataFrame],
    model_path: Union[Path, str] = "model.py",
):
    """Generate pydantic model from a dictionnary of pandas dataframes.

    Parameters
    ----------
    database : Dict[str, pd.DataFrame]
        A analytical database: eg. loaded from a dictionnary of csvs
    model_path : Union[Path, str], optional
        The path to the generated datamodel python file, by default "model.py"
    """
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


def read_database(
    dir2database: Union[str, Path], nrows: int = None
) -> Dict[str, pd.DataFrame]:
    """Read an analytical database from a directory.

    Parameters
    ----------
    dir2database : Union[str, Path]
        Directory containing the database.
        Format supports: csv.
    nrows : int, optional
        Limit the number of rows, by default None
    Returns
    -------
    Dict[str, pd.DataFrame]

    Examples
    --------
    >>> from pydmo import read_database, DIR2TEST_DATABASE
    >>> database = read_database(DIR2TEST_DATABASE)
    >>>  for k,v in database.items():
            print(f"{k}: {v.columns}")
    admissions: Index(['ROW_ID', 'SUBJECT_ID', 'HADM_ID', 'ADMITTIME', 'DISCHTIME',
       'DEATHTIME', 'ADMISSION_TYPE', 'ADMISSION_LOCATION',
       'DISCHARGE_LOCATION', 'INSURANCE', 'LANGUAGE', 'RELIGION',
       'MARITAL_STATUS', 'ETHNICITY', 'EDREGTIME', 'EDOUTTIME', 'DIAGNOSIS',
       'HOSPITAL_EXPIRE_FLAG', 'HAS_CHARTEVENTS_DATA'],
      dtype='object')
    patients: Index(['ROW_ID', 'SUBJECT_ID', 'GENDER', 'DOB', 'DOD', 'DOD_HOSP', 'DOD_SSN',
       'EXPIRE_FLAG'],
      dtype='object')
    """
    database_dict = {}

    for file in Path(dir2database).iterdir():
        if file.suffix == ".csv":
            database_dict[file.stem.lower()] = pd.read_csv(file, nrows=nrows)
    return database_dict
