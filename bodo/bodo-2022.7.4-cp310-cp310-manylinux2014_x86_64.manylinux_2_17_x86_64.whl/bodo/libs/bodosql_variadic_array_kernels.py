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
    for bmn__qyv in range(len(A)):
        if isinstance(A[bmn__qyv], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.coalesce',
                ['A'], bmn__qyv, container_length=len(A))

    def impl(A):
        return coalesce_util(A)
    return impl


def coalesce_util(A):
    return


@overload(coalesce_util, no_unliteral=True)
def overload_coalesce_util(A):
    if len(A) == 0:
        raise_bodo_error('Cannot coalesce 0 columns')
    bgnn__lriy = None
    rsgq__slyo = []
    for bmn__qyv in range(len(A)):
        if A[bmn__qyv] == bodo.none:
            rsgq__slyo.append(bmn__qyv)
        elif not bodo.utils.utils.is_array_typ(A[bmn__qyv]):
            for hua__gyf in range(bmn__qyv + 1, len(A)):
                rsgq__slyo.append(hua__gyf)
                if bodo.utils.utils.is_array_typ(A[hua__gyf]):
                    bgnn__lriy = f'A[{hua__gyf}]'
            break
    unzv__jkj = [f'A{bmn__qyv}' for bmn__qyv in range(len(A)) if bmn__qyv
         not in rsgq__slyo]
    hphui__ykky = [A[bmn__qyv] for bmn__qyv in range(len(A)) if bmn__qyv not in
        rsgq__slyo]
    jfgy__kpz = [False] * (len(A) - len(rsgq__slyo))
    mkjz__twjrx = ''
    sanwy__yvgic = True
    yvan__avtps = False
    jpp__njb = 0
    for bmn__qyv in range(len(A)):
        if bmn__qyv in rsgq__slyo:
            jpp__njb += 1
            continue
        elif bodo.utils.utils.is_array_typ(A[bmn__qyv]):
            qnsuk__hckdn = 'if' if sanwy__yvgic else 'elif'
            mkjz__twjrx += (
                f'{qnsuk__hckdn} not bodo.libs.array_kernels.isna(A{bmn__qyv}, i):\n'
                )
            mkjz__twjrx += f'   res[i] = arg{bmn__qyv - jpp__njb}\n'
            sanwy__yvgic = False
        else:
            assert not yvan__avtps, 'should not encounter more than one scalar due to dead column pruning'
            if sanwy__yvgic:
                mkjz__twjrx += f'res[i] = arg{bmn__qyv - jpp__njb}\n'
            else:
                mkjz__twjrx += 'else:\n'
                mkjz__twjrx += f'   res[i] = arg{bmn__qyv - jpp__njb}\n'
            yvan__avtps = True
            break
    if not yvan__avtps:
        if not sanwy__yvgic:
            mkjz__twjrx += 'else:\n'
            mkjz__twjrx += '   bodo.libs.array_kernels.setna(res, i)'
        else:
            mkjz__twjrx += 'bodo.libs.array_kernels.setna(res, i)'
    cuzkv__wcajg = 'A'
    itzed__akf = {f'A{bmn__qyv}': f'A[{bmn__qyv}]' for bmn__qyv in range(
        len(A)) if bmn__qyv not in rsgq__slyo}
    dobsc__iris = get_common_broadcasted_type(hphui__ykky, 'COALESCE')
    return gen_vectorized(unzv__jkj, hphui__ykky, jfgy__kpz, mkjz__twjrx,
        dobsc__iris, cuzkv__wcajg, itzed__akf, bgnn__lriy,
        support_dict_encoding=False)


@numba.generated_jit(nopython=True)
def decode(A):
    if not isinstance(A, (types.Tuple, types.UniTuple)):
        raise_bodo_error('Decode argument must be a tuple')
    for bmn__qyv in range(len(A)):
        if isinstance(A[bmn__qyv], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.decode',
                ['A'], bmn__qyv, container_length=len(A))

    def impl(A):
        return decode_util(A)
    return impl


@numba.generated_jit(nopython=True)
def decode_util(A):
    if len(A) < 3:
        raise_bodo_error('Need at least 3 arguments to DECODE')
    unzv__jkj = [f'A{bmn__qyv}' for bmn__qyv in range(len(A))]
    hphui__ykky = [A[bmn__qyv] for bmn__qyv in range(len(A))]
    jfgy__kpz = [False] * len(A)
    mkjz__twjrx = ''
    for bmn__qyv in range(1, len(A) - 1, 2):
        qnsuk__hckdn = 'if' if len(mkjz__twjrx) == 0 else 'elif'
        if A[bmn__qyv + 1] == bodo.none:
            pje__xig = '   bodo.libs.array_kernels.setna(res, i)\n'
        elif bodo.utils.utils.is_array_typ(A[bmn__qyv + 1]):
            pje__xig = (
                f'   if bodo.libs.array_kernels.isna({unzv__jkj[bmn__qyv + 1]}, i):\n'
                )
            pje__xig += f'      bodo.libs.array_kernels.setna(res, i)\n'
            pje__xig += f'   else:\n'
            pje__xig += f'      res[i] = arg{bmn__qyv + 1}\n'
        else:
            pje__xig = f'   res[i] = arg{bmn__qyv + 1}\n'
        if A[0] == bodo.none and (bodo.utils.utils.is_array_typ(A[bmn__qyv]
            ) or A[bmn__qyv] == bodo.none):
            if A[bmn__qyv] == bodo.none:
                mkjz__twjrx += f'{qnsuk__hckdn} True:\n'
                mkjz__twjrx += pje__xig
                break
            else:
                mkjz__twjrx += f"""{qnsuk__hckdn} bodo.libs.array_kernels.isna({unzv__jkj[bmn__qyv]}, i):
"""
                mkjz__twjrx += pje__xig
        elif A[0] == bodo.none:
            pass
        elif bodo.utils.utils.is_array_typ(A[0]):
            if bodo.utils.utils.is_array_typ(A[bmn__qyv]):
                mkjz__twjrx += f"""{qnsuk__hckdn} (bodo.libs.array_kernels.isna({unzv__jkj[0]}, i) and bodo.libs.array_kernels.isna({unzv__jkj[bmn__qyv]}, i)) or (not bodo.libs.array_kernels.isna({unzv__jkj[0]}, i) and not bodo.libs.array_kernels.isna({unzv__jkj[bmn__qyv]}, i) and arg0 == arg{bmn__qyv}):
"""
                mkjz__twjrx += pje__xig
            elif A[bmn__qyv] == bodo.none:
                mkjz__twjrx += (
                    f'{qnsuk__hckdn} bodo.libs.array_kernels.isna({unzv__jkj[0]}, i):\n'
                    )
                mkjz__twjrx += pje__xig
            else:
                mkjz__twjrx += f"""{qnsuk__hckdn} (not bodo.libs.array_kernels.isna({unzv__jkj[0]}, i)) and arg0 == arg{bmn__qyv}:
"""
                mkjz__twjrx += pje__xig
        elif A[bmn__qyv] == bodo.none:
            pass
        elif bodo.utils.utils.is_array_typ(A[bmn__qyv]):
            mkjz__twjrx += f"""{qnsuk__hckdn} (not bodo.libs.array_kernels.isna({unzv__jkj[bmn__qyv]}, i)) and arg0 == arg{bmn__qyv}:
"""
            mkjz__twjrx += pje__xig
        else:
            mkjz__twjrx += f'{qnsuk__hckdn} arg0 == arg{bmn__qyv}:\n'
            mkjz__twjrx += pje__xig
    if len(mkjz__twjrx) > 0:
        mkjz__twjrx += 'else:\n'
    if len(A) % 2 == 0 and A[-1] != bodo.none:
        if bodo.utils.utils.is_array_typ(A[-1]):
            mkjz__twjrx += (
                f'   if bodo.libs.array_kernels.isna({unzv__jkj[-1]}, i):\n')
            mkjz__twjrx += '      bodo.libs.array_kernels.setna(res, i)\n'
            mkjz__twjrx += '   else:\n'
        mkjz__twjrx += f'      res[i] = arg{len(A) - 1}'
    else:
        mkjz__twjrx += '   bodo.libs.array_kernels.setna(res, i)'
    cuzkv__wcajg = 'A'
    itzed__akf = {f'A{bmn__qyv}': f'A[{bmn__qyv}]' for bmn__qyv in range(
        len(A))}
    if len(hphui__ykky) % 2 == 0:
        cxxm__ofp = [hphui__ykky[0]] + hphui__ykky[1:-1:2]
        arsvb__wth = hphui__ykky[2::2] + [hphui__ykky[-1]]
    else:
        cxxm__ofp = [hphui__ykky[0]] + hphui__ykky[1::2]
        arsvb__wth = hphui__ykky[2::2]
    uylwf__dksuh = get_common_broadcasted_type(cxxm__ofp, 'DECODE')
    dobsc__iris = get_common_broadcasted_type(arsvb__wth, 'DECODE')
    if dobsc__iris == bodo.none:
        dobsc__iris = uylwf__dksuh
    xhoo__qwpbq = bodo.utils.utils.is_array_typ(A[0]
        ) and bodo.none not in cxxm__ofp and len(hphui__ykky) % 2 == 1
    return gen_vectorized(unzv__jkj, hphui__ykky, jfgy__kpz, mkjz__twjrx,
        dobsc__iris, cuzkv__wcajg, itzed__akf, support_dict_encoding=
        xhoo__qwpbq)
