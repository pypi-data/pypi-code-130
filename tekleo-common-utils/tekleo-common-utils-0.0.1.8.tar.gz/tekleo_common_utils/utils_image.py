from PIL import Image as image_pil_main
from PIL import ExifTags
from PIL.Image import Image, Exif
import cv2
import numpy
import requests
import tempfile
import io
import base64
from numpy import ndarray
from injectable import injectable, autowired, Autowired
from tekleo_common_utils.utils_random import UtilsRandom
from pillow_heif import register_heif_opener


@injectable
class UtilsImage:
    @autowired
    def __init__(self, utils_random: Autowired(UtilsRandom)):
        self.utils_random = utils_random
        register_heif_opener()

    def convert_image_pil_to_image_cv(self, image_pil: Image) -> ndarray:
        return cv2.cvtColor(numpy.array(image_pil), cv2.COLOR_RGB2BGR)

    def convert_image_cv_to_image_pil(self, image_cv: ndarray) -> Image:
        return image_pil_main.fromarray(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))

    def open_image_pil(self, image_path: str, rotate_to_exif_orientation: bool = True) -> Image:
        # Open the image
        image_pil = image_pil_main.open(image_path)
        # If we need to rotate in align with exif data - rotate first and clear exif after
        if rotate_to_exif_orientation:
            image_pil = self.rotate_image_according_to_exif_orientation(image_pil)
            image_pil = self.clear_exif_data(image_pil)
        return image_pil

    def open_image_cv(self, image_path: str, rotate_to_exif_orientation: bool = True) -> ndarray:
        return self.convert_image_pil_to_image_cv(self.open_image_pil(image_path, rotate_to_exif_orientation=rotate_to_exif_orientation))

    def save_image_pil(self, image_pil: Image, image_path: str, quality: int = 100, subsampling: int = 0) -> str:
        # Make sure the image is in RGB mode
        image_extension = image_path.split('.')[-1].lower()
        if image_extension in ['jpg', 'jpeg'] and image_pil.mode.lower() != 'rgb':
            image_pil = image_pil.convert('RGB')
        image_pil.save(image_path, quality=quality, subsampling=subsampling)
        return image_path

    def save_image_cv(self, image_cv: ndarray, image_path: str) -> str:
        return self.save_image_pil(self.convert_image_cv_to_image_pil(image_cv), image_path)

    def debug_image_pil(self, image_pil: Image, window_name: str = 'Debug Image'):
        image_cv = self.convert_image_pil_to_image_cv(image_pil)
        self.debug_image_cv(image_cv, window_name)

    def debug_image_cv(self, image_cv: ndarray, window_name: str = 'Debug Image'):
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.imshow(window_name, image_cv)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def download_image_pil(self, image_url: str, timeout_in_seconds: int = 90) -> Image:
        # Make request
        headers = {'User-Agent': self.utils_random.get_random_user_agent()}
        response = requests.get(image_url, headers=headers, timeout=timeout_in_seconds, stream=True)
        response.raise_for_status()

        # Download the image into buffer
        buffer = tempfile.SpooledTemporaryFile(max_size=1e9)
        downloaded = 0
        for chunk in response.iter_content(chunk_size=1024):
            downloaded += len(chunk)
            buffer.write(chunk)
        buffer.seek(0)

        # Convert buffer to image
        image = image_pil_main.open(io.BytesIO(buffer.read()))
        return image

    def encode_image_pil_as_base64(self, image_pil: Image) -> str:
        bytes_io = io.BytesIO()
        image_pil.save(bytes_io, format="PNG")
        return str(base64.b64encode(bytes_io.getvalue()), 'utf-8')

    def decode_image_pil_from_base64(self, image_base64: str) -> Image:
        image_bytes = base64.b64decode(bytes(image_base64, 'utf-8'))
        image = image_pil_main.open(io.BytesIO(image_bytes))
        return image

    def clear_exif_data(self, image_pil: Image) -> Image:
        del image_pil.info['exif']
        return image_pil

    def rotate_image_according_to_exif_orientation(self, image_pil: Image) -> Image:
        # Check that we have valid exif data
        exif_data = image_pil.getexif()
        if len(exif_data) == 0:
            return image_pil

        # Make sure we have orientation key
        orientation_key = [k for k in ExifTags.TAGS.keys() if ExifTags.TAGS[k] == 'Orientation'][0]
        if orientation_key not in exif_data:
            return image_pil

        # Get value and rotate accordingly
        orientation_value = exif_data.get(orientation_key)
        if orientation_value == 3:
            image_pil = image_pil.rotate(180, expand=True)
        elif orientation_value == 6:
            image_pil = image_pil.rotate(270, expand=True)
        elif orientation_value == 8:
            image_pil = image_pil.rotate(90, expand=True)

        return image_pil

    def convert_to_jpg(self, image_path: str) -> str:
        extension = image_path.split('.')[-1]
        new_image_path = image_path.replace('.' + extension, '.jpg')
        image_pil = self.open_image_pil(image_path)
        self.save_image_pil(image_pil, new_image_path)
        return new_image_path
