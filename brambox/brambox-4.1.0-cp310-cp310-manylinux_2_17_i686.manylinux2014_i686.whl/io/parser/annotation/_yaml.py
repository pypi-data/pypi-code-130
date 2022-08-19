#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
import logging
import numpy as np
import pandas as pd
from ._base import AnnotationParser, ParserType

try:
    import yaml
except ImportError:
    yaml = None

__all__ = ['YamlParser']
log = logging.getLogger(__name__)


class YamlParser(AnnotationParser):
    """
    This parser generates a lightweight human readable annotation format.
    With only one file for the entire dataset, this format will save you precious HDD space and will also be parsed faster.

    Keyword Args:
        keep_ignore (boolean): Whether are not you want to save/load the ignore value; Default **False**
        precision (integer): The number of decimals for the coordinates; Default **None** (save as int)

    Example:
        >>> annotations.yaml
            img1:
              car:
                - coords: [x,y,w,h]
                  lost: False
                  difficult: True
                  occluded_fraction: 50.123
                  truncated_fraction: 0.0
              person:
                - id: 1
                  coords: [x,y,w,h]
                  lost: False
                  difficult: False
                  occluded_fraction: 0.0
                  truncated_fraction: 10.0
                - id: 2
                  coords: [x,y,w,h]
                  lost: False
                  difficult: False
                  occluded_fraction: 0.0
                  truncated_fraction: 0.0
            img2:
              car:
                - coords: [x,y,w,h]
                  lost: True
                  difficult: False
                  occluded_fraction: 90.0
                  truncated_fraction: 76.0
    """
    parser_type = ParserType.SINGLE_FILE
    serialize_group = 'image'   # Easier to generate one string per image to add image label
    extension = '.yaml'

    def __init__(self, keep_ignore=False, precision=None):
        if yaml is None:
            raise ImportError('Pyyaml package not found. Please install it in order to use this parser!')

        super().__init__()
        self.add_column('segmentation', pd.NA)
        self.keep_ignore = keep_ignore
        self.precision = precision

    def serialize(self, df):
        result = {}

        has_segmentation = 'segmentation' in df.columns and str(df['segmentation'].dtype) == 'geos'
        if has_segmentation:
            df['segmentation'] = df['segmentation'].geos.to_wkt()

        for row in df.itertuples():
            box = {
                'coords': [round(row.x_top_left, self.precision), round(row.y_top_left, self.precision),
                           round(row.width, self.precision), round(row.height, self.precision)],
                'lost': row.lost,
                'difficult': row.difficult,
                'occluded_fraction': row.occluded*100,
                'truncated_fraction': row.truncated*100,
            }
            if not np.isnan(row.id):
                box['id'] = int(row.id)
            if self.keep_ignore:
                box['ignore'] = row.ignore
            if has_segmentation:
                box['segmentation'] = row.segmentation

            class_label = row.class_label if row.class_label != '' else '?'
            if class_label not in result:
                result[class_label] = [box]
            else:
                result[class_label].append(box)

        return yaml.dump({df.name: result}, default_flow_style=None)

    def deserialize(self, rawdata, file_id=None):
        yml_obj = yaml.safe_load(rawdata)

        for file_id in yml_obj:
            self.append_image(file_id)
            if yml_obj[file_id] is not None:
                for class_label, annos in yml_obj[file_id].items():
                    for anno in annos:
                        data = {
                            'class_label': '' if class_label == '?' else class_label,
                            'x_top_left': float(anno['coords'][0]),
                            'y_top_left': float(anno['coords'][1]),
                            'width': float(anno['coords'][2]),
                            'height': float(anno['coords'][3]),
                            'occluded': anno['occluded_fraction'] / 100,
                            'truncated': anno['truncated_fraction'] / 100,
                            'lost': anno['lost'],
                            'difficult': anno['difficult'],
                            'ignore': anno['ignore'] if 'ignore' in anno and self.keep_ignore else False,
                        }
                        if 'id' in anno:
                            data['id'] = anno['id']
                        if 'segmentation' in anno:
                            data['segmentation'] = None if anno['segmentation'] == 'null' else anno['segmentation']

                        self.append(file_id, **data)

    def post_deserialize(self, df):
        if df['segmentation'].isna().all():
            return df.drop(columns='segmentation')
        else:
            df['segmentation'] = df['segmentation'].geos.to_geos()
            return df
