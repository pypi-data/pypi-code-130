import lib_compute.typon_math as typon_math
import lib_py_parse.utils.parsing_utils as parsing_utils

def deserialize_data(target_buffer, target_type, buffer_index, classes):
    if buffer_index + 1 > len(target_buffer):
        return [None, -1]
    target_type = target_type.replace(' ', '')
    if target_type == 'bool':
        result = ( target_buffer[buffer_index] == chr(1) )
        return [ result, buffer_index + 1 ]
    if target_type == 'char':
        result = target_buffer[buffer_index]
        return [ result, buffer_index + 1 ]
    if target_type == 'int':
        if buffer_index + 8 > len(target_buffer):
            return [None, -1]
        result = typon_math.deserialize_int(target_buffer[ buffer_index : buffer_index + 8])
        return [ result, buffer_index + 8 ]
    if target_type == 'dbl':
        if buffer_index + 8 > len(target_buffer):
            return [None, -1]
        result = typon_math.deserialize_dbl(target_buffer[ buffer_index : buffer_index + 8])
        return [ result, buffer_index + 8 ]
    if target_type == 'str':
        if buffer_index + 8 > len(target_buffer):
            return [None, -1]
        str_len = typon_math.deserialize_int(target_buffer[ buffer_index : buffer_index + 8])
        if buffer_index + 8 + str_len > len(target_buffer):
            return [None, -1]
        result = target_buffer[ buffer_index + 8 : buffer_index + 8 + str_len ]
        return [ result, buffer_index + 8 + str_len]
    if target_type[0:4] == 'vec[':
        if buffer_index + 8 > len(target_buffer):
            return [None, -1]
        item_type = target_type[4:-1]
        vec_len = typon_math.deserialize_int(target_buffer[ buffer_index : buffer_index + 8])
        result = []
        buffer_index_vec = buffer_index + 8
        for i in range(0, vec_len):
            value, buffer_index_vec = deserialize_data( target_buffer, item_type, buffer_index_vec, classes )
            if buffer_index_vec == -1:
                return [None, -1]
            result.append(value)
        return [ result, buffer_index_vec ]
    if target_type[0:5] in ['hmap[', 'smap[']:
        if buffer_index + 8 > len(target_buffer):
            return [None, -1]
        delimited_types = target_type[5:-1]
        key_type, value_type = parsing_utils.read_delimited_types(delimited_types)
        map_len = typon_math.deserialize_int(target_buffer[ buffer_index : buffer_index + 8])
        result = {}
        buffer_index_map = buffer_index + 8
        for i in range(0, map_len):
            key_ref, buffer_index_map = deserialize_data( target_buffer, key_type, buffer_index_map, classes )
            if buffer_index_map == -1:
                return [None, -1]
            value_ref, buffer_index_map = deserialize_data( target_buffer, value_type, buffer_index_map, classes )
            if buffer_index_map == -1:
                return [None, -1]
            result[key_ref] = value_ref
        return [ result, buffer_index_map ]
    if target_type[0:5] == 'tupl[':
        delimited_types = target_type[5:-1]
        typon_tuple_types = parsing_utils.read_delimited_types(delimited_types)
        result = []
        buffer_index_tupl = buffer_index
        for i in range(0, len(typon_tuple_types)):
            value_ref, buffer_index_tupl = deserialize_data( target_buffer, typon_tuple_types[i], buffer_index_tupl, classes )
            if buffer_index_tupl == -1:
                return [None, -1]
            result.append(value_ref)
        return [ result, buffer_index_tupl ]
    if target_type in classes:
        class_items = classes[target_type]
        buffer_index_class = buffer_index
        constructor_args = []
        for attr_name in class_items:
            attr_type = class_items[attr_name]
            attr_ref, buffer_index_class = deserialize_data( target_buffer, attr_type, buffer_index_class, classes )
            if buffer_index_class == -1:
                return [None, -1]
            constructor_args.append(attr_ref)
        result = eval( f'{target_type}(*constructor_args)')
        return [ result, buffer_index_class ]
    raise Exception(f'unverified type in fxn deserialize_data: {target_type}')
