from numba.core import cgutils, types
from numba.extending import NativeValue, box, make_attribute_wrapper, models, register_model, typeof_impl, unbox


def install_py_obj_class(types_name, module, python_type=None, class_name=
    None, model_name=None):
    class_name = ''.join(map(str.title, types_name.split('_'))
        ) if class_name is None else class_name
    model_name = f'{class_name}Model' if model_name is None else model_name
    vliay__ydb = f'class {class_name}(types.Opaque):\n'
    vliay__ydb += f'    def __init__(self):\n'
    vliay__ydb += f"       types.Opaque.__init__(self, name='{class_name}')\n"
    vliay__ydb += f'    def __reduce__(self):\n'
    vliay__ydb += (
        f"        return (types.Opaque, ('{class_name}',), self.__dict__)\n")
    ocb__ksb = {}
    exec(vliay__ydb, {'types': types, 'models': models}, ocb__ksb)
    zyofx__wcy = ocb__ksb[class_name]
    setattr(module, class_name, zyofx__wcy)
    class_instance = zyofx__wcy()
    setattr(types, types_name, class_instance)
    vliay__ydb = f'class {model_name}(models.StructModel):\n'
    vliay__ydb += f'    def __init__(self, dmm, fe_type):\n'
    vliay__ydb += f'        members = [\n'
    vliay__ydb += (
        f"            ('meminfo', types.MemInfoPointer({types_name})),\n")
    vliay__ydb += f"            ('pyobj', types.voidptr),\n"
    vliay__ydb += f'        ]\n'
    vliay__ydb += (
        f'        models.StructModel.__init__(self, dmm, fe_type, members)\n')
    exec(vliay__ydb, {'types': types, 'models': models, types_name:
        class_instance}, ocb__ksb)
    zlbz__ehp = ocb__ksb[model_name]
    setattr(module, model_name, zlbz__ehp)
    register_model(zyofx__wcy)(zlbz__ehp)
    make_attribute_wrapper(zyofx__wcy, 'pyobj', '_pyobj')
    if python_type is not None:
        typeof_impl.register(python_type)(lambda val, c: class_instance)
    unbox(zyofx__wcy)(unbox_py_obj)
    box(zyofx__wcy)(box_py_obj)
    return zyofx__wcy


def box_py_obj(typ, val, c):
    iqdhc__nart = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = iqdhc__nart.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


def unbox_py_obj(typ, obj, c):
    iqdhc__nart = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    iqdhc__nart.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    iqdhc__nart.pyobj = obj
    return NativeValue(iqdhc__nart._getvalue())
