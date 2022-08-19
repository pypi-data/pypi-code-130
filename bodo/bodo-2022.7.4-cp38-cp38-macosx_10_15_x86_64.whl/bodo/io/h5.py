"""
Analysis and transformation for HDF5 support.
"""
import types as pytypes
import numba
from numba.core import ir, types
from numba.core.ir_utils import compile_to_numba_ir, find_callname, find_const, get_definition, guard, replace_arg_nodes, require
import bodo
import bodo.io
from bodo.utils.transform import get_const_value_inner


class H5_IO:

    def __init__(self, func_ir, _locals, flags, arg_types):
        self.func_ir = func_ir
        self.locals = _locals
        self.flags = flags
        self.arg_types = arg_types

    def handle_possible_h5_read(self, assign, lhs, rhs):
        bwptr__qca = self._get_h5_type(lhs, rhs)
        if bwptr__qca is not None:
            vumeu__toodb = str(bwptr__qca.dtype)
            zvyo__zlzqg = 'def _h5_read_impl(dset, index):\n'
            zvyo__zlzqg += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(bwptr__qca.ndim, vumeu__toodb))
            bdhm__sub = {}
            exec(zvyo__zlzqg, {}, bdhm__sub)
            ulz__uwdun = bdhm__sub['_h5_read_impl']
            ums__jcxwi = compile_to_numba_ir(ulz__uwdun, {'bodo': bodo}
                ).blocks.popitem()[1]
            uvrz__jxm = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(ums__jcxwi, [rhs.value, uvrz__jxm])
            sechu__uqi = ums__jcxwi.body[:-3]
            sechu__uqi[-1].target = assign.target
            return sechu__uqi
        return None

    def _get_h5_type(self, lhs, rhs):
        bwptr__qca = self._get_h5_type_locals(lhs)
        if bwptr__qca is not None:
            return bwptr__qca
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        uvrz__jxm = rhs.index if rhs.op == 'getitem' else rhs.index_var
        gpoc__pebk = guard(find_const, self.func_ir, uvrz__jxm)
        require(not isinstance(gpoc__pebk, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            twz__xhgh = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            ktnl__gqqy = get_const_value_inner(self.func_ir, twz__xhgh,
                arg_types=self.arg_types)
            obj_name_list.append(ktnl__gqqy)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        ovz__tvf = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        auey__smda = h5py.File(ovz__tvf, 'r')
        elpo__pje = auey__smda
        for ktnl__gqqy in obj_name_list:
            elpo__pje = elpo__pje[ktnl__gqqy]
        require(isinstance(elpo__pje, h5py.Dataset))
        gtefc__zquvk = len(elpo__pje.shape)
        gmjfz__kaat = numba.np.numpy_support.from_dtype(elpo__pje.dtype)
        auey__smda.close()
        return types.Array(gmjfz__kaat, gtefc__zquvk, 'C')

    def _get_h5_type_locals(self, varname):
        ygj__rweoz = self.locals.pop(varname, None)
        if ygj__rweoz is None and varname is not None:
            ygj__rweoz = self.flags.h5_types.get(varname, None)
        return ygj__rweoz
