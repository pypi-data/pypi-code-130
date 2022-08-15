"""
Implements array kernels that are specific to BodoSQL which have a variable
number of arguments
"""
from numba.core import types
from numba.extending import overload
import bodo
from bodo.libs.bodosql_array_kernel_utils import *
from bodo.utils.typing import raise_bodo_error


def coalesce(A):
    return


@overload(coalesce)
def overload_coalesce(A):
    if not isinstance(A, (types.Tuple, types.UniTuple)):
        raise_bodo_error('Coalesce argument must be a tuple')
    for voff__qkndk in range(len(A)):
        if isinstance(A[voff__qkndk], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.coalesce',
                ['A'], voff__qkndk, container_length=len(A))

    def impl(A):
        return coalesce_util(A)
    return impl


def coalesce_util(A):
    return


@overload(coalesce_util, no_unliteral=True)
def overload_coalesce_util(A):
    if len(A) == 0:
        raise_bodo_error('Cannot coalesce 0 columns')
    ktovx__gep = None
    pxkoi__dvpk = []
    for voff__qkndk in range(len(A)):
        if A[voff__qkndk] == bodo.none:
            pxkoi__dvpk.append(voff__qkndk)
        elif not bodo.utils.utils.is_array_typ(A[voff__qkndk]):
            for jxddm__zpowg in range(voff__qkndk + 1, len(A)):
                pxkoi__dvpk.append(jxddm__zpowg)
                if bodo.utils.utils.is_array_typ(A[jxddm__zpowg]):
                    ktovx__gep = f'A[{jxddm__zpowg}]'
            break
    ixtne__uzpn = [f'A{voff__qkndk}' for voff__qkndk in range(len(A)) if 
        voff__qkndk not in pxkoi__dvpk]
    sxqw__whaam = [A[voff__qkndk] for voff__qkndk in range(len(A)) if 
        voff__qkndk not in pxkoi__dvpk]
    prlo__hraah = [False] * (len(A) - len(pxkoi__dvpk))
    ujrcq__goby = ''
    qld__mdtr = True
    vxl__tyurr = False
    xmhay__wyial = 0
    for voff__qkndk in range(len(A)):
        if voff__qkndk in pxkoi__dvpk:
            xmhay__wyial += 1
            continue
        elif bodo.utils.utils.is_array_typ(A[voff__qkndk]):
            mzwsd__rto = 'if' if qld__mdtr else 'elif'
            ujrcq__goby += (
                f'{mzwsd__rto} not bodo.libs.array_kernels.isna(A{voff__qkndk}, i):\n'
                )
            ujrcq__goby += f'   res[i] = arg{voff__qkndk - xmhay__wyial}\n'
            qld__mdtr = False
        else:
            assert not vxl__tyurr, 'should not encounter more than one scalar due to dead column pruning'
            if qld__mdtr:
                ujrcq__goby += f'res[i] = arg{voff__qkndk - xmhay__wyial}\n'
            else:
                ujrcq__goby += 'else:\n'
                ujrcq__goby += f'   res[i] = arg{voff__qkndk - xmhay__wyial}\n'
            vxl__tyurr = True
            break
    if not vxl__tyurr:
        if not qld__mdtr:
            ujrcq__goby += 'else:\n'
            ujrcq__goby += '   bodo.libs.array_kernels.setna(res, i)'
        else:
            ujrcq__goby += 'bodo.libs.array_kernels.setna(res, i)'
    gmm__gkxho = 'A'
    ocagr__onhdc = {f'A{voff__qkndk}': f'A[{voff__qkndk}]' for voff__qkndk in
        range(len(A)) if voff__qkndk not in pxkoi__dvpk}
    xohe__zke = get_common_broadcasted_type(sxqw__whaam, 'COALESCE')
    return gen_vectorized(ixtne__uzpn, sxqw__whaam, prlo__hraah,
        ujrcq__goby, xohe__zke, gmm__gkxho, ocagr__onhdc, ktovx__gep,
        support_dict_encoding=False)


@numba.generated_jit(nopython=True)
def decode(A):
    if not isinstance(A, (types.Tuple, types.UniTuple)):
        raise_bodo_error('Decode argument must be a tuple')
    for voff__qkndk in range(len(A)):
        if isinstance(A[voff__qkndk], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.decode',
                ['A'], voff__qkndk, container_length=len(A))

    def impl(A):
        return decode_util(A)
    return impl


@numba.generated_jit(nopython=True)
def decode_util(A):
    if len(A) < 3:
        raise_bodo_error('Need at least 3 arguments to DECODE')
    ixtne__uzpn = [f'A{voff__qkndk}' for voff__qkndk in range(len(A))]
    sxqw__whaam = [A[voff__qkndk] for voff__qkndk in range(len(A))]
    prlo__hraah = [False] * len(A)
    ujrcq__goby = ''
    for voff__qkndk in range(1, len(A) - 1, 2):
        mzwsd__rto = 'if' if len(ujrcq__goby) == 0 else 'elif'
        if A[voff__qkndk + 1] == bodo.none:
            jfj__yiut = '   bodo.libs.array_kernels.setna(res, i)\n'
        elif bodo.utils.utils.is_array_typ(A[voff__qkndk + 1]):
            jfj__yiut = (
                f'   if bodo.libs.array_kernels.isna({ixtne__uzpn[voff__qkndk + 1]}, i):\n'
                )
            jfj__yiut += f'      bodo.libs.array_kernels.setna(res, i)\n'
            jfj__yiut += f'   else:\n'
            jfj__yiut += f'      res[i] = arg{voff__qkndk + 1}\n'
        else:
            jfj__yiut = f'   res[i] = arg{voff__qkndk + 1}\n'
        if A[0] == bodo.none and (bodo.utils.utils.is_array_typ(A[
            voff__qkndk]) or A[voff__qkndk] == bodo.none):
            if A[voff__qkndk] == bodo.none:
                ujrcq__goby += f'{mzwsd__rto} True:\n'
                ujrcq__goby += jfj__yiut
                break
            else:
                ujrcq__goby += f"""{mzwsd__rto} bodo.libs.array_kernels.isna({ixtne__uzpn[voff__qkndk]}, i):
"""
                ujrcq__goby += jfj__yiut
        elif A[0] == bodo.none:
            pass
        elif bodo.utils.utils.is_array_typ(A[0]):
            if bodo.utils.utils.is_array_typ(A[voff__qkndk]):
                ujrcq__goby += f"""{mzwsd__rto} (bodo.libs.array_kernels.isna({ixtne__uzpn[0]}, i) and bodo.libs.array_kernels.isna({ixtne__uzpn[voff__qkndk]}, i)) or (not bodo.libs.array_kernels.isna({ixtne__uzpn[0]}, i) and not bodo.libs.array_kernels.isna({ixtne__uzpn[voff__qkndk]}, i) and arg0 == arg{voff__qkndk}):
"""
                ujrcq__goby += jfj__yiut
            elif A[voff__qkndk] == bodo.none:
                ujrcq__goby += (
                    f'{mzwsd__rto} bodo.libs.array_kernels.isna({ixtne__uzpn[0]}, i):\n'
                    )
                ujrcq__goby += jfj__yiut
            else:
                ujrcq__goby += f"""{mzwsd__rto} (not bodo.libs.array_kernels.isna({ixtne__uzpn[0]}, i)) and arg0 == arg{voff__qkndk}:
"""
                ujrcq__goby += jfj__yiut
        elif A[voff__qkndk] == bodo.none:
            pass
        elif bodo.utils.utils.is_array_typ(A[voff__qkndk]):
            ujrcq__goby += f"""{mzwsd__rto} (not bodo.libs.array_kernels.isna({ixtne__uzpn[voff__qkndk]}, i)) and arg0 == arg{voff__qkndk}:
"""
            ujrcq__goby += jfj__yiut
        else:
            ujrcq__goby += f'{mzwsd__rto} arg0 == arg{voff__qkndk}:\n'
            ujrcq__goby += jfj__yiut
    if len(ujrcq__goby) > 0:
        ujrcq__goby += 'else:\n'
    if len(A) % 2 == 0 and A[-1] != bodo.none:
        if bodo.utils.utils.is_array_typ(A[-1]):
            ujrcq__goby += (
                f'   if bodo.libs.array_kernels.isna({ixtne__uzpn[-1]}, i):\n')
            ujrcq__goby += '      bodo.libs.array_kernels.setna(res, i)\n'
            ujrcq__goby += '   else:\n'
        ujrcq__goby += f'      res[i] = arg{len(A) - 1}'
    else:
        ujrcq__goby += '   bodo.libs.array_kernels.setna(res, i)'
    gmm__gkxho = 'A'
    ocagr__onhdc = {f'A{voff__qkndk}': f'A[{voff__qkndk}]' for voff__qkndk in
        range(len(A))}
    if len(sxqw__whaam) % 2 == 0:
        ksgfh__jmkf = [sxqw__whaam[0]] + sxqw__whaam[1:-1:2]
        znydw__dwa = sxqw__whaam[2::2] + [sxqw__whaam[-1]]
    else:
        ksgfh__jmkf = [sxqw__whaam[0]] + sxqw__whaam[1::2]
        znydw__dwa = sxqw__whaam[2::2]
    pdc__oxru = get_common_broadcasted_type(ksgfh__jmkf, 'DECODE')
    xohe__zke = get_common_broadcasted_type(znydw__dwa, 'DECODE')
    if xohe__zke == bodo.none:
        xohe__zke = pdc__oxru
    iyxg__phsz = bodo.utils.utils.is_array_typ(A[0]
        ) and bodo.none not in ksgfh__jmkf and len(sxqw__whaam) % 2 == 1
    return gen_vectorized(ixtne__uzpn, sxqw__whaam, prlo__hraah,
        ujrcq__goby, xohe__zke, gmm__gkxho, ocagr__onhdc,
        support_dict_encoding=iyxg__phsz)
