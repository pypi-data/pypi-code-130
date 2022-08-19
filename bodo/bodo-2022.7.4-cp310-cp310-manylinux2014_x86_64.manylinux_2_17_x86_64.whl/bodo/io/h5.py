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
        xidol__krtv = self._get_h5_type(lhs, rhs)
        if xidol__krtv is not None:
            qkp__pqhd = str(xidol__krtv.dtype)
            xyxag__zruko = 'def _h5_read_impl(dset, index):\n'
            xyxag__zruko += (
                "  arr = bodo.io.h5_api.h5_read_dummy(dset, {}, '{}', index)\n"
                .format(xidol__krtv.ndim, qkp__pqhd))
            wpwr__tsna = {}
            exec(xyxag__zruko, {}, wpwr__tsna)
            gdeqn__gibl = wpwr__tsna['_h5_read_impl']
            kvy__zsp = compile_to_numba_ir(gdeqn__gibl, {'bodo': bodo}
                ).blocks.popitem()[1]
            iskdu__dfstn = rhs.index if rhs.op == 'getitem' else rhs.index_var
            replace_arg_nodes(kvy__zsp, [rhs.value, iskdu__dfstn])
            znnvn__qmqk = kvy__zsp.body[:-3]
            znnvn__qmqk[-1].target = assign.target
            return znnvn__qmqk
        return None

    def _get_h5_type(self, lhs, rhs):
        xidol__krtv = self._get_h5_type_locals(lhs)
        if xidol__krtv is not None:
            return xidol__krtv
        return guard(self._infer_h5_typ, rhs)

    def _infer_h5_typ(self, rhs):
        require(rhs.op in ('getitem', 'static_getitem'))
        iskdu__dfstn = rhs.index if rhs.op == 'getitem' else rhs.index_var
        syuc__spxo = guard(find_const, self.func_ir, iskdu__dfstn)
        require(not isinstance(syuc__spxo, str))
        val_def = rhs
        obj_name_list = []
        while True:
            val_def = get_definition(self.func_ir, val_def.value)
            require(isinstance(val_def, ir.Expr))
            if val_def.op == 'call':
                return self._get_h5_type_file(val_def, obj_name_list)
            require(val_def.op in ('getitem', 'static_getitem'))
            zroyn__eikes = (val_def.index if val_def.op == 'getitem' else
                val_def.index_var)
            xkgbk__wqj = get_const_value_inner(self.func_ir, zroyn__eikes,
                arg_types=self.arg_types)
            obj_name_list.append(xkgbk__wqj)

    def _get_h5_type_file(self, val_def, obj_name_list):
        require(len(obj_name_list) > 0)
        require(find_callname(self.func_ir, val_def) == ('File', 'h5py'))
        require(len(val_def.args) > 0)
        ikzv__nwx = get_const_value_inner(self.func_ir, val_def.args[0],
            arg_types=self.arg_types)
        obj_name_list.reverse()
        import h5py
        gmr__vlj = h5py.File(ikzv__nwx, 'r')
        gumrs__ulkq = gmr__vlj
        for xkgbk__wqj in obj_name_list:
            gumrs__ulkq = gumrs__ulkq[xkgbk__wqj]
        require(isinstance(gumrs__ulkq, h5py.Dataset))
        vjann__wgqbw = len(gumrs__ulkq.shape)
        cqqk__ppz = numba.np.numpy_support.from_dtype(gumrs__ulkq.dtype)
        gmr__vlj.close()
        return types.Array(cqqk__ppz, vjann__wgqbw, 'C')

    def _get_h5_type_locals(self, varname):
        ssz__zapr = self.locals.pop(varname, None)
        if ssz__zapr is None and varname is not None:
            ssz__zapr = self.flags.h5_types.get(varname, None)
        return ssz__zapr
