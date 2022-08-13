# importattrs
#########################################################################################################
# Imports
from ..error import ImportAttrs, ImportFile
from .importfile import importfile as __importfile
from .importfile import SfcparseFileData as __SfcparseFileData

#########################################################################################################
# Import Attributes from File
class __SfcparseDummy:
    class Class: """dummy class for hinting"""

def importattrs(filename: str, class_object: '__SfcparseDummy.Class') -> None:
    """
    Import saved attributes from file back into a custom class. This is done in-place

    Enter filename as str, Pass custom class object.

    [Example Use]

    importattrs('path/of/filename', 'class_object')
    """
    # Error Checks
    __err_msg_type_str_filename = "Only str is allowed for filename"
    __err_msg_type_class_obj = "Only a custom class object is allowed for class_object"
    __err_msg_type_sfcparse_obj = "Please use 'importfile' function to properly import a SfcparseFileData object"

    if not isinstance(filename, str): raise ImportAttrs(__err_msg_type_str_filename, f'\nFILE: "{filename}"')
    
    if (isinstance(class_object, str)) \
    or (isinstance(class_object, int)) \
    or (isinstance(class_object, float)) \
    or (isinstance(class_object, bool)) \
    or (isinstance(class_object, list)) \
    or (isinstance(class_object, tuple)) \
    or (isinstance(class_object, set)) \
    or (isinstance(class_object, dict)) \
    or (isinstance(class_object, type(None))) \
    or (isinstance(class_object, bytes)) \
    or (isinstance(class_object, complex)) \
    or (isinstance(class_object, range)) \
    or (isinstance(class_object, frozenset)) \
    or (isinstance(class_object, bytearray)) \
    or (isinstance(class_object, memoryview)):
        raise ImportAttrs(__err_msg_type_class_obj, f'\nFILE: "{filename}" \nDATA: {class_object}')

    if isinstance(class_object, __SfcparseFileData):
        raise ImportAttrs(__err_msg_type_sfcparse_obj, f'\nFILE: "{filename}" \nDATA: {class_object}')


    # Import Attrs from File and Inject into Given Class Object

    # Skip Key
    __skip_object_key = ('_SfcparseFileData', '__sfcparse_file_format_id')

    # Import Attrs
    try:
        __imported_data = __importfile(filename)
        for key,value in __imported_data.__dict__.items():
            if key.startswith(__skip_object_key): continue
            setattr(class_object, key, value)
    except ImportFile as __err_msg:
        raise ImportAttrs(__err_msg, '')

    return None
