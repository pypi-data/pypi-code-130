from numba.core import cgutils, types
from numba.extending import NativeValue, box, make_attribute_wrapper, models, register_model, typeof_impl, unbox


def install_py_obj_class(types_name, module, python_type=None, class_name=
    None, model_name=None):
    class_name = ''.join(map(str.title, types_name.split('_'))
        ) if class_name is None else class_name
    model_name = f'{class_name}Model' if model_name is None else model_name
    lmch__bplm = f'class {class_name}(types.Opaque):\n'
    lmch__bplm += f'    def __init__(self):\n'
    lmch__bplm += f"       types.Opaque.__init__(self, name='{class_name}')\n"
    lmch__bplm += f'    def __reduce__(self):\n'
    lmch__bplm += (
        f"        return (types.Opaque, ('{class_name}',), self.__dict__)\n")
    luz__ucrx = {}
    exec(lmch__bplm, {'types': types, 'models': models}, luz__ucrx)
    tdpf__rxf = luz__ucrx[class_name]
    setattr(module, class_name, tdpf__rxf)
    class_instance = tdpf__rxf()
    setattr(types, types_name, class_instance)
    lmch__bplm = f'class {model_name}(models.StructModel):\n'
    lmch__bplm += f'    def __init__(self, dmm, fe_type):\n'
    lmch__bplm += f'        members = [\n'
    lmch__bplm += (
        f"            ('meminfo', types.MemInfoPointer({types_name})),\n")
    lmch__bplm += f"            ('pyobj', types.voidptr),\n"
    lmch__bplm += f'        ]\n'
    lmch__bplm += (
        f'        models.StructModel.__init__(self, dmm, fe_type, members)\n')
    exec(lmch__bplm, {'types': types, 'models': models, types_name:
        class_instance}, luz__ucrx)
    uwh__hxcq = luz__ucrx[model_name]
    setattr(module, model_name, uwh__hxcq)
    register_model(tdpf__rxf)(uwh__hxcq)
    make_attribute_wrapper(tdpf__rxf, 'pyobj', '_pyobj')
    if python_type is not None:
        typeof_impl.register(python_type)(lambda val, c: class_instance)
    unbox(tdpf__rxf)(unbox_py_obj)
    box(tdpf__rxf)(box_py_obj)
    return tdpf__rxf


def box_py_obj(typ, val, c):
    hnix__csfj = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = hnix__csfj.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


def unbox_py_obj(typ, obj, c):
    hnix__csfj = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    hnix__csfj.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    hnix__csfj.pyobj = obj
    return NativeValue(hnix__csfj._getvalue())
