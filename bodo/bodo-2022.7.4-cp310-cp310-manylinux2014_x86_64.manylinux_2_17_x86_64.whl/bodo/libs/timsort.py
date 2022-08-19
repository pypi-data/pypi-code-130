import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    fdosb__toca = hi - lo
    if fdosb__toca < 2:
        return
    if fdosb__toca < MIN_MERGE:
        hsb__bcmt = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + hsb__bcmt, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    zdgg__feoqj = minRunLength(fdosb__toca)
    while True:
        iyaw__lxkg = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if iyaw__lxkg < zdgg__feoqj:
            ewggu__pcq = (fdosb__toca if fdosb__toca <= zdgg__feoqj else
                zdgg__feoqj)
            binarySort(key_arrs, lo, lo + ewggu__pcq, lo + iyaw__lxkg, data)
            iyaw__lxkg = ewggu__pcq
        stackSize = pushRun(stackSize, runBase, runLen, lo, iyaw__lxkg)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += iyaw__lxkg
        fdosb__toca -= iyaw__lxkg
        if fdosb__toca == 0:
            break
    assert lo == hi
    stackSize, tmpLength, tmp, tmp_data, minGallop = mergeForceCollapse(
        stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
        tmp_data, minGallop)
    assert stackSize == 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def binarySort(key_arrs, lo, hi, start, data):
    assert lo <= start and start <= hi
    if start == lo:
        start += 1
    while start < hi:
        zhe__kqhlm = getitem_arr_tup(key_arrs, start)
        ybj__ftefu = getitem_arr_tup(data, start)
        rzcy__quz = lo
        ogp__ehjm = start
        assert rzcy__quz <= ogp__ehjm
        while rzcy__quz < ogp__ehjm:
            iqg__sgiyu = rzcy__quz + ogp__ehjm >> 1
            if zhe__kqhlm < getitem_arr_tup(key_arrs, iqg__sgiyu):
                ogp__ehjm = iqg__sgiyu
            else:
                rzcy__quz = iqg__sgiyu + 1
        assert rzcy__quz == ogp__ehjm
        n = start - rzcy__quz
        copyRange_tup(key_arrs, rzcy__quz, key_arrs, rzcy__quz + 1, n)
        copyRange_tup(data, rzcy__quz, data, rzcy__quz + 1, n)
        setitem_arr_tup(key_arrs, rzcy__quz, zhe__kqhlm)
        setitem_arr_tup(data, rzcy__quz, ybj__ftefu)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    wcsmq__dax = lo + 1
    if wcsmq__dax == hi:
        return 1
    if getitem_arr_tup(key_arrs, wcsmq__dax) < getitem_arr_tup(key_arrs, lo):
        wcsmq__dax += 1
        while wcsmq__dax < hi and getitem_arr_tup(key_arrs, wcsmq__dax
            ) < getitem_arr_tup(key_arrs, wcsmq__dax - 1):
            wcsmq__dax += 1
        reverseRange(key_arrs, lo, wcsmq__dax, data)
    else:
        wcsmq__dax += 1
        while wcsmq__dax < hi and getitem_arr_tup(key_arrs, wcsmq__dax
            ) >= getitem_arr_tup(key_arrs, wcsmq__dax - 1):
            wcsmq__dax += 1
    return wcsmq__dax - lo


@numba.njit(no_cpython_wrapper=True, cache=True)
def reverseRange(key_arrs, lo, hi, data):
    hi -= 1
    while lo < hi:
        swap_arrs(key_arrs, lo, hi)
        swap_arrs(data, lo, hi)
        lo += 1
        hi -= 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def minRunLength(n):
    assert n >= 0
    ckgx__axcvs = 0
    while n >= MIN_MERGE:
        ckgx__axcvs |= n & 1
        n >>= 1
    return n + ckgx__axcvs


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    zkvuu__mlpzu = len(key_arrs[0])
    tmpLength = (zkvuu__mlpzu >> 1 if zkvuu__mlpzu < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    gyea__pla = (5 if zkvuu__mlpzu < 120 else 10 if zkvuu__mlpzu < 1542 else
        19 if zkvuu__mlpzu < 119151 else 40)
    runBase = np.empty(gyea__pla, np.int64)
    runLen = np.empty(gyea__pla, np.int64)
    return stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def pushRun(stackSize, runBase, runLen, runBase_val, runLen_val):
    runBase[stackSize] = runBase_val
    runLen[stackSize] = runLen_val
    stackSize += 1
    return stackSize


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeCollapse(stackSize, runBase, runLen, key_arrs, data, tmpLength,
    tmp, tmp_data, minGallop):
    while stackSize > 1:
        n = stackSize - 2
        if n >= 1 and runLen[n - 1] <= runLen[n] + runLen[n + 1
            ] or n >= 2 and runLen[n - 2] <= runLen[n] + runLen[n - 1]:
            if runLen[n - 1] < runLen[n + 1]:
                n -= 1
        elif runLen[n] > runLen[n + 1]:
            break
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeAt(stackSize,
            runBase, runLen, key_arrs, data, tmpLength, tmp, tmp_data,
            minGallop, n)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeForceCollapse(stackSize, runBase, runLen, key_arrs, data,
    tmpLength, tmp, tmp_data, minGallop):
    while stackSize > 1:
        n = stackSize - 2
        if n > 0 and runLen[n - 1] < runLen[n + 1]:
            n -= 1
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeAt(stackSize,
            runBase, runLen, key_arrs, data, tmpLength, tmp, tmp_data,
            minGallop, n)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeAt(stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
    tmp_data, minGallop, i):
    assert stackSize >= 2
    assert i >= 0
    assert i == stackSize - 2 or i == stackSize - 3
    base1 = runBase[i]
    len1 = runLen[i]
    base2 = runBase[i + 1]
    len2 = runLen[i + 1]
    assert len1 > 0 and len2 > 0
    assert base1 + len1 == base2
    runLen[i] = len1 + len2
    if i == stackSize - 3:
        runBase[i + 1] = runBase[i + 2]
        runLen[i + 1] = runLen[i + 2]
    stackSize -= 1
    nkm__mzapf = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert nkm__mzapf >= 0
    base1 += nkm__mzapf
    len1 -= nkm__mzapf
    if len1 == 0:
        return stackSize, tmpLength, tmp, tmp_data, minGallop
    len2 = gallopLeft(getitem_arr_tup(key_arrs, base1 + len1 - 1), key_arrs,
        base2, len2, len2 - 1)
    assert len2 >= 0
    if len2 == 0:
        return stackSize, tmpLength, tmp, tmp_data, minGallop
    if len1 <= len2:
        tmpLength, tmp, tmp_data = ensureCapacity(tmpLength, tmp, tmp_data,
            key_arrs, data, len1)
        minGallop = mergeLo(key_arrs, data, tmp, tmp_data, minGallop, base1,
            len1, base2, len2)
    else:
        tmpLength, tmp, tmp_data = ensureCapacity(tmpLength, tmp, tmp_data,
            key_arrs, data, len2)
        minGallop = mergeHi(key_arrs, data, tmp, tmp_data, minGallop, base1,
            len1, base2, len2)
    return stackSize, tmpLength, tmp, tmp_data, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopLeft(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    xgmbz__rhth = 0
    nzr__cuhod = 1
    if key > getitem_arr_tup(arr, base + hint):
        swny__gpnal = _len - hint
        while nzr__cuhod < swny__gpnal and key > getitem_arr_tup(arr, base +
            hint + nzr__cuhod):
            xgmbz__rhth = nzr__cuhod
            nzr__cuhod = (nzr__cuhod << 1) + 1
            if nzr__cuhod <= 0:
                nzr__cuhod = swny__gpnal
        if nzr__cuhod > swny__gpnal:
            nzr__cuhod = swny__gpnal
        xgmbz__rhth += hint
        nzr__cuhod += hint
    else:
        swny__gpnal = hint + 1
        while nzr__cuhod < swny__gpnal and key <= getitem_arr_tup(arr, base +
            hint - nzr__cuhod):
            xgmbz__rhth = nzr__cuhod
            nzr__cuhod = (nzr__cuhod << 1) + 1
            if nzr__cuhod <= 0:
                nzr__cuhod = swny__gpnal
        if nzr__cuhod > swny__gpnal:
            nzr__cuhod = swny__gpnal
        tmp = xgmbz__rhth
        xgmbz__rhth = hint - nzr__cuhod
        nzr__cuhod = hint - tmp
    assert -1 <= xgmbz__rhth and xgmbz__rhth < nzr__cuhod and nzr__cuhod <= _len
    xgmbz__rhth += 1
    while xgmbz__rhth < nzr__cuhod:
        svjcm__dkd = xgmbz__rhth + (nzr__cuhod - xgmbz__rhth >> 1)
        if key > getitem_arr_tup(arr, base + svjcm__dkd):
            xgmbz__rhth = svjcm__dkd + 1
        else:
            nzr__cuhod = svjcm__dkd
    assert xgmbz__rhth == nzr__cuhod
    return nzr__cuhod


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    nzr__cuhod = 1
    xgmbz__rhth = 0
    if key < getitem_arr_tup(arr, base + hint):
        swny__gpnal = hint + 1
        while nzr__cuhod < swny__gpnal and key < getitem_arr_tup(arr, base +
            hint - nzr__cuhod):
            xgmbz__rhth = nzr__cuhod
            nzr__cuhod = (nzr__cuhod << 1) + 1
            if nzr__cuhod <= 0:
                nzr__cuhod = swny__gpnal
        if nzr__cuhod > swny__gpnal:
            nzr__cuhod = swny__gpnal
        tmp = xgmbz__rhth
        xgmbz__rhth = hint - nzr__cuhod
        nzr__cuhod = hint - tmp
    else:
        swny__gpnal = _len - hint
        while nzr__cuhod < swny__gpnal and key >= getitem_arr_tup(arr, base +
            hint + nzr__cuhod):
            xgmbz__rhth = nzr__cuhod
            nzr__cuhod = (nzr__cuhod << 1) + 1
            if nzr__cuhod <= 0:
                nzr__cuhod = swny__gpnal
        if nzr__cuhod > swny__gpnal:
            nzr__cuhod = swny__gpnal
        xgmbz__rhth += hint
        nzr__cuhod += hint
    assert -1 <= xgmbz__rhth and xgmbz__rhth < nzr__cuhod and nzr__cuhod <= _len
    xgmbz__rhth += 1
    while xgmbz__rhth < nzr__cuhod:
        svjcm__dkd = xgmbz__rhth + (nzr__cuhod - xgmbz__rhth >> 1)
        if key < getitem_arr_tup(arr, base + svjcm__dkd):
            nzr__cuhod = svjcm__dkd
        else:
            xgmbz__rhth = svjcm__dkd + 1
    assert xgmbz__rhth == nzr__cuhod
    return nzr__cuhod


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeLo(key_arrs, data, tmp, tmp_data, minGallop, base1, len1, base2, len2
    ):
    assert len1 > 0 and len2 > 0 and base1 + len1 == base2
    arr = key_arrs
    arr_data = data
    copyRange_tup(arr, base1, tmp, 0, len1)
    copyRange_tup(arr_data, base1, tmp_data, 0, len1)
    cursor1 = 0
    cursor2 = base2
    dest = base1
    setitem_arr_tup(arr, dest, getitem_arr_tup(arr, cursor2))
    copyElement_tup(arr_data, cursor2, arr_data, dest)
    cursor2 += 1
    dest += 1
    len2 -= 1
    if len2 == 0:
        copyRange_tup(tmp, cursor1, arr, dest, len1)
        copyRange_tup(tmp_data, cursor1, arr_data, dest, len1)
        return minGallop
    if len1 == 1:
        copyRange_tup(arr, cursor2, arr, dest, len2)
        copyRange_tup(arr_data, cursor2, arr_data, dest, len2)
        copyElement_tup(tmp, cursor1, arr, dest + len2)
        copyElement_tup(tmp_data, cursor1, arr_data, dest + len2)
        return minGallop
    len1, len2, cursor1, cursor2, dest, minGallop = mergeLo_inner(key_arrs,
        data, tmp_data, len1, len2, tmp, cursor1, cursor2, dest, minGallop)
    minGallop = 1 if minGallop < 1 else minGallop
    if len1 == 1:
        assert len2 > 0
        copyRange_tup(arr, cursor2, arr, dest, len2)
        copyRange_tup(arr_data, cursor2, arr_data, dest, len2)
        copyElement_tup(tmp, cursor1, arr, dest + len2)
        copyElement_tup(tmp_data, cursor1, arr_data, dest + len2)
    elif len1 == 0:
        raise ValueError('Comparison method violates its general contract!')
    else:
        assert len2 == 0
        assert len1 > 1
        copyRange_tup(tmp, cursor1, arr, dest, len1)
        copyRange_tup(tmp_data, cursor1, arr_data, dest, len1)
    return minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeLo_inner(arr, arr_data, tmp_data, len1, len2, tmp, cursor1,
    cursor2, dest, minGallop):
    while True:
        tdn__vfmga = 0
        cuhir__zla = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                cuhir__zla += 1
                tdn__vfmga = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                tdn__vfmga += 1
                cuhir__zla = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not tdn__vfmga | cuhir__zla < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            tdn__vfmga = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if tdn__vfmga != 0:
                copyRange_tup(tmp, cursor1, arr, dest, tdn__vfmga)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, tdn__vfmga)
                dest += tdn__vfmga
                cursor1 += tdn__vfmga
                len1 -= tdn__vfmga
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            cuhir__zla = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if cuhir__zla != 0:
                copyRange_tup(arr, cursor2, arr, dest, cuhir__zla)
                copyRange_tup(arr_data, cursor2, arr_data, dest, cuhir__zla)
                dest += cuhir__zla
                cursor2 += cuhir__zla
                len2 -= cuhir__zla
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor1, arr, dest)
            copyElement_tup(tmp_data, cursor1, arr_data, dest)
            cursor1 += 1
            dest += 1
            len1 -= 1
            if len1 == 1:
                return len1, len2, cursor1, cursor2, dest, minGallop
            minGallop -= 1
            if not tdn__vfmga >= MIN_GALLOP | cuhir__zla >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeHi(key_arrs, data, tmp, tmp_data, minGallop, base1, len1, base2, len2
    ):
    assert len1 > 0 and len2 > 0 and base1 + len1 == base2
    arr = key_arrs
    arr_data = data
    copyRange_tup(arr, base2, tmp, 0, len2)
    copyRange_tup(arr_data, base2, tmp_data, 0, len2)
    cursor1 = base1 + len1 - 1
    cursor2 = len2 - 1
    dest = base2 + len2 - 1
    copyElement_tup(arr, cursor1, arr, dest)
    copyElement_tup(arr_data, cursor1, arr_data, dest)
    cursor1 -= 1
    dest -= 1
    len1 -= 1
    if len1 == 0:
        copyRange_tup(tmp, 0, arr, dest - (len2 - 1), len2)
        copyRange_tup(tmp_data, 0, arr_data, dest - (len2 - 1), len2)
        return minGallop
    if len2 == 1:
        dest -= len1
        cursor1 -= len1
        copyRange_tup(arr, cursor1 + 1, arr, dest + 1, len1)
        copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1, len1)
        copyElement_tup(tmp, cursor2, arr, dest)
        copyElement_tup(tmp_data, cursor2, arr_data, dest)
        return minGallop
    len1, len2, tmp, cursor1, cursor2, dest, minGallop = mergeHi_inner(key_arrs
        , data, tmp_data, base1, len1, len2, tmp, cursor1, cursor2, dest,
        minGallop)
    minGallop = 1 if minGallop < 1 else minGallop
    if len2 == 1:
        assert len1 > 0
        dest -= len1
        cursor1 -= len1
        copyRange_tup(arr, cursor1 + 1, arr, dest + 1, len1)
        copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1, len1)
        copyElement_tup(tmp, cursor2, arr, dest)
        copyElement_tup(tmp_data, cursor2, arr_data, dest)
    elif len2 == 0:
        raise ValueError('Comparison method violates its general contract!')
    else:
        assert len1 == 0
        assert len2 > 0
        copyRange_tup(tmp, 0, arr, dest - (len2 - 1), len2)
        copyRange_tup(tmp_data, 0, arr_data, dest - (len2 - 1), len2)
    return minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def mergeHi_inner(arr, arr_data, tmp_data, base1, len1, len2, tmp, cursor1,
    cursor2, dest, minGallop):
    while True:
        tdn__vfmga = 0
        cuhir__zla = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                tdn__vfmga += 1
                cuhir__zla = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                cuhir__zla += 1
                tdn__vfmga = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not tdn__vfmga | cuhir__zla < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            tdn__vfmga = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if tdn__vfmga != 0:
                dest -= tdn__vfmga
                cursor1 -= tdn__vfmga
                len1 -= tdn__vfmga
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, tdn__vfmga)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    tdn__vfmga)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            cuhir__zla = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if cuhir__zla != 0:
                dest -= cuhir__zla
                cursor2 -= cuhir__zla
                len2 -= cuhir__zla
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, cuhir__zla)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    cuhir__zla)
                if len2 <= 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor1, arr, dest)
            copyElement_tup(arr_data, cursor1, arr_data, dest)
            cursor1 -= 1
            dest -= 1
            len1 -= 1
            if len1 == 0:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            minGallop -= 1
            if not tdn__vfmga >= MIN_GALLOP | cuhir__zla >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    fprur__mjw = len(key_arrs[0])
    if tmpLength < minCapacity:
        cjil__cba = minCapacity
        cjil__cba |= cjil__cba >> 1
        cjil__cba |= cjil__cba >> 2
        cjil__cba |= cjil__cba >> 4
        cjil__cba |= cjil__cba >> 8
        cjil__cba |= cjil__cba >> 16
        cjil__cba += 1
        if cjil__cba < 0:
            cjil__cba = minCapacity
        else:
            cjil__cba = min(cjil__cba, fprur__mjw >> 1)
        tmp = alloc_arr_tup(cjil__cba, key_arrs)
        tmp_data = alloc_arr_tup(cjil__cba, data)
        tmpLength = cjil__cba
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        yxl__lewog = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = yxl__lewog


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    jqi__xukei = arr_tup.count
    bmtm__ikpoz = 'def f(arr_tup, lo, hi):\n'
    for i in range(jqi__xukei):
        bmtm__ikpoz += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        bmtm__ikpoz += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        bmtm__ikpoz += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    bmtm__ikpoz += '  return\n'
    uauka__tfvf = {}
    exec(bmtm__ikpoz, {}, uauka__tfvf)
    edqfw__pfh = uauka__tfvf['f']
    return edqfw__pfh


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    jqi__xukei = src_arr_tup.count
    assert jqi__xukei == dst_arr_tup.count
    bmtm__ikpoz = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(jqi__xukei):
        bmtm__ikpoz += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    bmtm__ikpoz += '  return\n'
    uauka__tfvf = {}
    exec(bmtm__ikpoz, {'copyRange': copyRange}, uauka__tfvf)
    jtnc__kxgjy = uauka__tfvf['f']
    return jtnc__kxgjy


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    jqi__xukei = src_arr_tup.count
    assert jqi__xukei == dst_arr_tup.count
    bmtm__ikpoz = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(jqi__xukei):
        bmtm__ikpoz += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    bmtm__ikpoz += '  return\n'
    uauka__tfvf = {}
    exec(bmtm__ikpoz, {'copyElement': copyElement}, uauka__tfvf)
    jtnc__kxgjy = uauka__tfvf['f']
    return jtnc__kxgjy


def getitem_arr_tup(arr_tup, ind):
    hbl__vnbbi = [arr[ind] for arr in arr_tup]
    return tuple(hbl__vnbbi)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    jqi__xukei = arr_tup.count
    bmtm__ikpoz = 'def f(arr_tup, ind):\n'
    bmtm__ikpoz += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(jqi__xukei)]), ',' if jqi__xukei == 1 else '')
    uauka__tfvf = {}
    exec(bmtm__ikpoz, {}, uauka__tfvf)
    qolg__jerp = uauka__tfvf['f']
    return qolg__jerp


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, dlbxg__okoe in zip(arr_tup, val_tup):
        arr[ind] = dlbxg__okoe


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    jqi__xukei = arr_tup.count
    bmtm__ikpoz = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(jqi__xukei):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            bmtm__ikpoz += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            bmtm__ikpoz += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    bmtm__ikpoz += '  return\n'
    uauka__tfvf = {}
    exec(bmtm__ikpoz, {}, uauka__tfvf)
    qolg__jerp = uauka__tfvf['f']
    return qolg__jerp


def test():
    import time
    wmv__wun = time.time()
    qseu__jtq = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((qseu__jtq,), 0, 3, data)
    print('compile time', time.time() - wmv__wun)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    bfqad__czw = np.random.ranf(n)
    tdc__phsc = pd.DataFrame({'A': bfqad__czw, 'B': data[0], 'C': data[1]})
    wmv__wun = time.time()
    ukw__iijia = tdc__phsc.sort_values('A', inplace=False)
    sqywg__iiqhw = time.time()
    sort((bfqad__czw,), 0, n, data)
    print('Bodo', time.time() - sqywg__iiqhw, 'Numpy', sqywg__iiqhw - wmv__wun)
    np.testing.assert_almost_equal(data[0], ukw__iijia.B.values)
    np.testing.assert_almost_equal(data[1], ukw__iijia.C.values)


if __name__ == '__main__':
    test()
