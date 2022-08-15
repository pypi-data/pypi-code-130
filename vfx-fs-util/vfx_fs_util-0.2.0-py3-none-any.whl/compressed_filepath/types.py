from ._base import CompressedFilepath
from ..config import COMPRESSED_FILEPATH_TYPES


class CompressedFilepathFactory(object):

    @staticmethod
    def make_cls(name, class_config, parent_cls='CompressedFilepath'):

        # I want to protect against bad configs
        parent_cls = parent_cls or 'CompressedFilepath'
        parent_cls = globals().get(parent_cls)
        if not parent_cls:
            parent_cls = parent_cls = globals().get('CompressedFilepath')

        class_data = {
           'TEMPLATE_STRINGS': tuple(class_config.get('filepath_attributes_parsing', [])),
           'STR_REPR_FORMAT': class_config.get('str_repr_format', '')
        }

        return type(name, (parent_cls,), class_data)


# Load any types from config
for _name, _data in COMPRESSED_FILEPATH_TYPES.items():

    _compressed_filepath = CompressedFilepathFactory.make_cls(
        name=_name,
        class_config=_data,
        parent_cls=_data.get('parent_class')
    )
    globals()[_name] = _compressed_filepath


# Subclassing below ##############################
