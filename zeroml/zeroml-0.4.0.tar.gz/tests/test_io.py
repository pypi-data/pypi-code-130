import numpy as np
import PIL.Image

from zeroml.io.image import save_array_image, save_pil


def test_save_pillow_image_random_name(random_pil_image, tmp_path):

    fp = save_pil(random_pil_image, tmp_path)
    image = PIL.Image.open(fp)

    assert image.size == random_pil_image.size


def test_save_pillow_image_with_name(random_pil_image, tmp_path):

    fp = save_pil(random_pil_image, tmp_path, file_name='ok.png')
    image = PIL.Image.open(fp)

    assert 'ok.png' in str(fp)

    assert image.size == random_pil_image.size


def test_save_numpy_image(tmp_path):
    image = np.random.randn(224, 224, 3).astype("uint8")
    fp = save_array_image(image, tmp_path)
    image = PIL.Image.open(fp)

    assert image.size == (224, 224)
