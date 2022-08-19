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
    for wegl__wkcpf in range(len(A)):
        if isinstance(A[wegl__wkcpf], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.coalesce',
                ['A'], wegl__wkcpf, container_length=len(A))

    def impl(A):
        return coalesce_util(A)
    return impl


def coalesce_util(A):
    return


@overload(coalesce_util, no_unliteral=True)
def overload_coalesce_util(A):
    if len(A) == 0:
        raise_bodo_error('Cannot coalesce 0 columns')
    wgp__unfy = None
    igk__mkxd = []
    for wegl__wkcpf in range(len(A)):
        if A[wegl__wkcpf] == bodo.none:
            igk__mkxd.append(wegl__wkcpf)
        elif not bodo.utils.utils.is_array_typ(A[wegl__wkcpf]):
            for nokxt__xmw in range(wegl__wkcpf + 1, len(A)):
                igk__mkxd.append(nokxt__xmw)
                if bodo.utils.utils.is_array_typ(A[nokxt__xmw]):
                    wgp__unfy = f'A[{nokxt__xmw}]'
            break
    dztuv__cnvma = [f'A{wegl__wkcpf}' for wegl__wkcpf in range(len(A)) if 
        wegl__wkcpf not in igk__mkxd]
    iabe__obed = [A[wegl__wkcpf] for wegl__wkcpf in range(len(A)) if 
        wegl__wkcpf not in igk__mkxd]
    fivh__vjqzi = [False] * (len(A) - len(igk__mkxd))
    ucqr__guri = ''
    tdcl__hiog = True
    kzopm__uvr = False
    nfla__gdxm = 0
    for wegl__wkcpf in range(len(A)):
        if wegl__wkcpf in igk__mkxd:
            nfla__gdxm += 1
            continue
        elif bodo.utils.utils.is_array_typ(A[wegl__wkcpf]):
            cxxlk__ahx = 'if' if tdcl__hiog else 'elif'
            ucqr__guri += (
                f'{cxxlk__ahx} not bodo.libs.array_kernels.isna(A{wegl__wkcpf}, i):\n'
                )
            ucqr__guri += f'   res[i] = arg{wegl__wkcpf - nfla__gdxm}\n'
            tdcl__hiog = False
        else:
            assert not kzopm__uvr, 'should not encounter more than one scalar due to dead column pruning'
            if tdcl__hiog:
                ucqr__guri += f'res[i] = arg{wegl__wkcpf - nfla__gdxm}\n'
            else:
                ucqr__guri += 'else:\n'
                ucqr__guri += f'   res[i] = arg{wegl__wkcpf - nfla__gdxm}\n'
            kzopm__uvr = True
            break
    if not kzopm__uvr:
        if not tdcl__hiog:
            ucqr__guri += 'else:\n'
            ucqr__guri += '   bodo.libs.array_kernels.setna(res, i)'
        else:
            ucqr__guri += 'bodo.libs.array_kernels.setna(res, i)'
    wakm__tauzr = 'A'
    qvalh__qvzdd = {f'A{wegl__wkcpf}': f'A[{wegl__wkcpf}]' for wegl__wkcpf in
        range(len(A)) if wegl__wkcpf not in igk__mkxd}
    skgi__cwckr = get_common_broadcasted_type(iabe__obed, 'COALESCE')
    return gen_vectorized(dztuv__cnvma, iabe__obed, fivh__vjqzi, ucqr__guri,
        skgi__cwckr, wakm__tauzr, qvalh__qvzdd, wgp__unfy,
        support_dict_encoding=False)


@numba.generated_jit(nopython=True)
def decode(A):
    if not isinstance(A, (types.Tuple, types.UniTuple)):
        raise_bodo_error('Decode argument must be a tuple')
    for wegl__wkcpf in range(len(A)):
        if isinstance(A[wegl__wkcpf], types.optional):
            return unopt_argument('bodo.libs.bodosql_array_kernels.decode',
                ['A'], wegl__wkcpf, container_length=len(A))

    def impl(A):
        return decode_util(A)
    return impl


@numba.generated_jit(nopython=True)
def decode_util(A):
    if len(A) < 3:
        raise_bodo_error('Need at least 3 arguments to DECODE')
    dztuv__cnvma = [f'A{wegl__wkcpf}' for wegl__wkcpf in range(len(A))]
    iabe__obed = [A[wegl__wkcpf] for wegl__wkcpf in range(len(A))]
    fivh__vjqzi = [False] * len(A)
    ucqr__guri = ''
    for wegl__wkcpf in range(1, len(A) - 1, 2):
        cxxlk__ahx = 'if' if len(ucqr__guri) == 0 else 'elif'
        if A[wegl__wkcpf + 1] == bodo.none:
            xlfp__panov = '   bodo.libs.array_kernels.setna(res, i)\n'
        elif bodo.utils.utils.is_array_typ(A[wegl__wkcpf + 1]):
            xlfp__panov = f"""   if bodo.libs.array_kernels.isna({dztuv__cnvma[wegl__wkcpf + 1]}, i):
"""
            xlfp__panov += f'      bodo.libs.array_kernels.setna(res, i)\n'
            xlfp__panov += f'   else:\n'
            xlfp__panov += f'      res[i] = arg{wegl__wkcpf + 1}\n'
        else:
            xlfp__panov = f'   res[i] = arg{wegl__wkcpf + 1}\n'
        if A[0] == bodo.none and (bodo.utils.utils.is_array_typ(A[
            wegl__wkcpf]) or A[wegl__wkcpf] == bodo.none):
            if A[wegl__wkcpf] == bodo.none:
                ucqr__guri += f'{cxxlk__ahx} True:\n'
                ucqr__guri += xlfp__panov
                break
            else:
                ucqr__guri += f"""{cxxlk__ahx} bodo.libs.array_kernels.isna({dztuv__cnvma[wegl__wkcpf]}, i):
"""
                ucqr__guri += xlfp__panov
        elif A[0] == bodo.none:
            pass
        elif bodo.utils.utils.is_array_typ(A[0]):
            if bodo.utils.utils.is_array_typ(A[wegl__wkcpf]):
                ucqr__guri += f"""{cxxlk__ahx} (bodo.libs.array_kernels.isna({dztuv__cnvma[0]}, i) and bodo.libs.array_kernels.isna({dztuv__cnvma[wegl__wkcpf]}, i)) or (not bodo.libs.array_kernels.isna({dztuv__cnvma[0]}, i) and not bodo.libs.array_kernels.isna({dztuv__cnvma[wegl__wkcpf]}, i) and arg0 == arg{wegl__wkcpf}):
"""
                ucqr__guri += xlfp__panov
            elif A[wegl__wkcpf] == bodo.none:
                ucqr__guri += (
                    f'{cxxlk__ahx} bodo.libs.array_kernels.isna({dztuv__cnvma[0]}, i):\n'
                    )
                ucqr__guri += xlfp__panov
            else:
                ucqr__guri += f"""{cxxlk__ahx} (not bodo.libs.array_kernels.isna({dztuv__cnvma[0]}, i)) and arg0 == arg{wegl__wkcpf}:
"""
                ucqr__guri += xlfp__panov
        elif A[wegl__wkcpf] == bodo.none:
            pass
        elif bodo.utils.utils.is_array_typ(A[wegl__wkcpf]):
            ucqr__guri += f"""{cxxlk__ahx} (not bodo.libs.array_kernels.isna({dztuv__cnvma[wegl__wkcpf]}, i)) and arg0 == arg{wegl__wkcpf}:
"""
            ucqr__guri += xlfp__panov
        else:
            ucqr__guri += f'{cxxlk__ahx} arg0 == arg{wegl__wkcpf}:\n'
            ucqr__guri += xlfp__panov
    if len(ucqr__guri) > 0:
        ucqr__guri += 'else:\n'
    if len(A) % 2 == 0 and A[-1] != bodo.none:
        if bodo.utils.utils.is_array_typ(A[-1]):
            ucqr__guri += (
                f'   if bodo.libs.array_kernels.isna({dztuv__cnvma[-1]}, i):\n'
                )
            ucqr__guri += '      bodo.libs.array_kernels.setna(res, i)\n'
            ucqr__guri += '   else:\n'
        ucqr__guri += f'      res[i] = arg{len(A) - 1}'
    else:
        ucqr__guri += '   bodo.libs.array_kernels.setna(res, i)'
    wakm__tauzr = 'A'
    qvalh__qvzdd = {f'A{wegl__wkcpf}': f'A[{wegl__wkcpf}]' for wegl__wkcpf in
        range(len(A))}
    if len(iabe__obed) % 2 == 0:
        fys__xfyae = [iabe__obed[0]] + iabe__obed[1:-1:2]
        ykq__tybb = iabe__obed[2::2] + [iabe__obed[-1]]
    else:
        fys__xfyae = [iabe__obed[0]] + iabe__obed[1::2]
        ykq__tybb = iabe__obed[2::2]
    wuxz__cbjo = get_common_broadcasted_type(fys__xfyae, 'DECODE')
    skgi__cwckr = get_common_broadcasted_type(ykq__tybb, 'DECODE')
    if skgi__cwckr == bodo.none:
        skgi__cwckr = wuxz__cbjo
    fcrs__edig = bodo.utils.utils.is_array_typ(A[0]
        ) and bodo.none not in fys__xfyae and len(iabe__obed) % 2 == 1
    return gen_vectorized(dztuv__cnvma, iabe__obed, fivh__vjqzi, ucqr__guri,
        skgi__cwckr, wakm__tauzr, qvalh__qvzdd, support_dict_encoding=
        fcrs__edig)
