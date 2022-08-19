#
#   Copyright EAVISE
#   Author: Maarten Vandersteegen
#   Author: Tanguy Ophoff
#
import os
import logging
import json
from ._base import AnnotationParser, ParserType

__all__ = ['CocoParser']
log = logging.getLogger(__name__)


class CocoParser(AnnotationParser):
    """
    This parser can parse annotations in the `MS COCO <coco_anno_>`_ format.
    This format consists of one json file for the whole dataset

    Args:
        add_image_dims (boolean, optional): If True, `image_width` and `image_height` columns are added to the deserialized data frame; Default **False**
        parse_image_names (boolean, optional): If True, we parse the image filenames from the data, otherwise we simply use image ids; Default **True**

    Note:
        The `iscrowd` flag is mapped to the `ignore` flag.

    Warning:
        This parser does not implement a serialization function
        as the COCO format has a lot of extra metadata which is not representable in the brambox data structure.
    """
    parser_type = ParserType.SINGLE_FILE
    extension = '.json'

    def __init__(self, add_image_dims=False, parse_image_names=True):
        super().__init__()
        self.add_image_dims = add_image_dims
        self.parse_image_names = parse_image_names
        if self.add_image_dims:
            self.add_column('image_width')
            self.add_column('image_height')

    def pre_serialize(self, df):
        raise NotImplementedError('This parser does not allow to save COCO json files, as there is too much different metadata in this format')

    def deserialize(self, rawdata, file_id=None):
        root = json.loads(rawdata)

        # create class label map for mapping class label ids to class label names
        class_label_map = {cat['id']: cat['name'] for cat in root['categories']}

        # create an image name map to map image ids to image names
        # and make sure all images are registered
        image_id_map = {}
        for image in root['images']:
            if self.parse_image_names:
                file_name = os.path.splitext(image['file_name'])[0]
                image_id_map[image['id']] = file_name
                self.append_image(file_name)
            else:
                self.append_image(image['id'])

        # optionally create image size map to map image ids to image width and height
        if self.add_image_dims:
            image_size_map = {img['id']: (img['width'], img['height']) for img in root['images']}

        # parse bboxes
        for anno in root['annotations']:
            image_id = image_id_map[anno['image_id']] if self.parse_image_names else anno['image_id']
            bbox = anno['bbox']

            data = {
                'class_label': class_label_map[anno['category_id']],
                'id': float(anno['id']),
                'x_top_left': float(bbox[0]),
                'y_top_left': float(bbox[1]),
                'width': float(bbox[2]),
                'height': float(bbox[3]),
                'ignore': (anno['iscrowd'] != 0),
            }
            if self.add_image_dims:
                image_size = image_size_map[anno['image_id']]
                data['image_width'] = (image_size[0])
                data['image_height'] = (image_size[1])

            self.append(image_id, **data)
