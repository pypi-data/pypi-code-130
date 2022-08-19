from numba.core import cgutils, types
from numba.extending import NativeValue, box, make_attribute_wrapper, models, register_model, typeof_impl, unbox


def install_py_obj_class(types_name, module, python_type=None, class_name=
    None, model_name=None):
    class_name = ''.join(map(str.title, types_name.split('_'))
        ) if class_name is None else class_name
    model_name = f'{class_name}Model' if model_name is None else model_name
    ura__vmnd = f'class {class_name}(types.Opaque):\n'
    ura__vmnd += f'    def __init__(self):\n'
    ura__vmnd += f"       types.Opaque.__init__(self, name='{class_name}')\n"
    ura__vmnd += f'    def __reduce__(self):\n'
    ura__vmnd += (
        f"        return (types.Opaque, ('{class_name}',), self.__dict__)\n")
    pvpqa__mksf = {}
    exec(ura__vmnd, {'types': types, 'models': models}, pvpqa__mksf)
    gjmbh__bupqh = pvpqa__mksf[class_name]
    setattr(module, class_name, gjmbh__bupqh)
    class_instance = gjmbh__bupqh()
    setattr(types, types_name, class_instance)
    ura__vmnd = f'class {model_name}(models.StructModel):\n'
    ura__vmnd += f'    def __init__(self, dmm, fe_type):\n'
    ura__vmnd += f'        members = [\n'
    ura__vmnd += (
        f"            ('meminfo', types.MemInfoPointer({types_name})),\n")
    ura__vmnd += f"            ('pyobj', types.voidptr),\n"
    ura__vmnd += f'        ]\n'
    ura__vmnd += (
        f'        models.StructModel.__init__(self, dmm, fe_type, members)\n')
    exec(ura__vmnd, {'types': types, 'models': models, types_name:
        class_instance}, pvpqa__mksf)
    lffc__roesy = pvpqa__mksf[model_name]
    setattr(module, model_name, lffc__roesy)
    register_model(gjmbh__bupqh)(lffc__roesy)
    make_attribute_wrapper(gjmbh__bupqh, 'pyobj', '_pyobj')
    if python_type is not None:
        typeof_impl.register(python_type)(lambda val, c: class_instance)
    unbox(gjmbh__bupqh)(unbox_py_obj)
    box(gjmbh__bupqh)(box_py_obj)
    return gjmbh__bupqh


def box_py_obj(typ, val, c):
    akhe__oha = cgutils.create_struct_proxy(typ)(c.context, c.builder, val)
    obj = akhe__oha.pyobj
    c.pyapi.incref(obj)
    c.context.nrt.decref(c.builder, typ, val)
    return obj


def unbox_py_obj(typ, obj, c):
    akhe__oha = cgutils.create_struct_proxy(typ)(c.context, c.builder)
    akhe__oha.meminfo = c.pyapi.nrt_meminfo_new_from_pyobject(c.context.
        get_constant_null(types.voidptr), obj)
    akhe__oha.pyobj = obj
    return NativeValue(akhe__oha._getvalue())
