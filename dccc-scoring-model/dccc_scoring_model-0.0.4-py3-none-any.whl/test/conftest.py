import pandas as pd
import pytest

from scoringmodel.config.core import DATASET_DIR, config


filepath = DATASET_DIR / config.app_config.test_data_file

@pytest.fixture()
def sample_input_data():
    return pd.read_csv(filepath, index_col=0)
