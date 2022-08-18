import uuid
from pathlib import Path

import numpy as np
import pandas as pd
import PIL.Image
import pytest


@pytest.fixture
def random_pil_image() -> PIL.Image:
    image = PIL.Image.fromarray(np.random.randn(224, 224, 3).astype("uint8"))
    return image


@pytest.fixture
def create_image_test_dataframe(tmp_path) -> (pd.DataFrame, Path):

    images = [PIL.Image.fromarray(np.ones((224, 224, 3)).astype("uint8")) for _ in range(10)]
    labels = [i for i in range(10)]
    fns = [str(uuid.uuid4()) + '.png' for _ in range(10)]
    print(fns)

    for image, f in zip(images, fns):
        image.save(tmp_path / f)

    df = pd.DataFrame({'labels': labels, 'file_names': fns})
    base_path = tmp_path
    return df, base_path
