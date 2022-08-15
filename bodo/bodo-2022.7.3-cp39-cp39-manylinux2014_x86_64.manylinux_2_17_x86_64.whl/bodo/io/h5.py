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
        hfg__wxju = self._get_h5_type(lhs, rhs)
        if hfg__wxju is not None:
            sct__yafhh = str(hfg__wxju.dtype)
            tftq__xvrvp = 'def _h5_read_impl(dset, index):\n'
            tftq__xvrvp += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(hfg__wxju.ndim, sct__yafhh))
            suoi__utilm = {}
            exec(tftq__xvrvp, {}, suoi__utilm)
            uzzr__nja = suoi__utilm['_h5_read_impl']
            xowxp__dbb = compile_to_numba_ir(uzzr__nja, {'bodo': bodo}
                ).blocks.popitem()[1]
            xxk__hyb = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(xowxp__dbb, [rhs.value, xxk__hyb])
            kkc__qfnp = xowxp__dbb.body[:-3]
            kkc__qfnp[-1].target = assign.target
            return kkc__qfnp
        return None

    def _get_h5_type(self, lhs, rhs):
        hfg__wxju = self._get_h5_type_locals(lhs)
        if hfg__wxju is not None:
            return hfg__wxju
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        xxk__hyb = rhs.index if rhs.op == 'getitem' else rhs.index_var
        ipnc__wflc = guard(find_const, self.func_ir, xxk__hyb)
        require(not isinstance(ipnc__wflc, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            bklbc__vqom = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            wxa__pto = get_const_value_inner(self.func_ir, bklbc__vqom,
                arg_types=self.arg_types)
            obj_name_list.append(wxa__pto)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        guhep__opx = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        vby__ncgr = h5py.File(guhep__opx, 'r')
        hzsp__gwul = vby__ncgr
        for wxa__pto in obj_name_list:
            hzsp__gwul = hzsp__gwul[wxa__pto]
        require(isinstance(hzsp__gwul, h5py.Dataset))
        xbc__mqtrw = len(hzsp__gwul.shape)
        equll__kctj = numba.np.numpy_support.from_dtype(hzsp__gwul.dtype)
        vby__ncgr.close()
        return types.Array(equll__kctj, xbc__mqtrw, 'C')

    def _get_h5_type_locals(self, varname):
        twp__iby = self.locals.pop(varname, None)
        if twp__iby is None and varname is not None:
            twp__iby = self.flags.h5_types.get(varname, None)
        return twp__iby
