import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    yhrpi__isum = hi - lo
    if yhrpi__isum < 2:
        return
    if yhrpi__isum < MIN_MERGE:
        ayz__hejd = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + ayz__hejd, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    oqjl__ufkv = minRunLength(yhrpi__isum)
    while True:
        bmz__pef = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if bmz__pef < oqjl__ufkv:
            yhi__amcz = (yhrpi__isum if yhrpi__isum <= oqjl__ufkv else
                oqjl__ufkv)
            binarySort(key_arrs, lo, lo + yhi__amcz, lo + bmz__pef, data)
            bmz__pef = yhi__amcz
        stackSize = pushRun(stackSize, runBase, runLen, lo, bmz__pef)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += bmz__pef
        yhrpi__isum -= bmz__pef
        if yhrpi__isum == 0:
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
        jzgy__stnu = getitem_arr_tup(key_arrs, start)
        xii__nogne = getitem_arr_tup(data, start)
        mvlmh__pnea = lo
        thiv__ukgb = start
        assert mvlmh__pnea <= thiv__ukgb
        while mvlmh__pnea < thiv__ukgb:
            nbqma__wezvz = mvlmh__pnea + thiv__ukgb >> 1
            if jzgy__stnu < getitem_arr_tup(key_arrs, nbqma__wezvz):
                thiv__ukgb = nbqma__wezvz
            else:
                mvlmh__pnea = nbqma__wezvz + 1
        assert mvlmh__pnea == thiv__ukgb
        n = start - mvlmh__pnea
        copyRange_tup(key_arrs, mvlmh__pnea, key_arrs, mvlmh__pnea + 1, n)
        copyRange_tup(data, mvlmh__pnea, data, mvlmh__pnea + 1, n)
        setitem_arr_tup(key_arrs, mvlmh__pnea, jzgy__stnu)
        setitem_arr_tup(data, mvlmh__pnea, xii__nogne)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    luh__bgzp = lo + 1
    if luh__bgzp == hi:
        return 1
    if getitem_arr_tup(key_arrs, luh__bgzp) < getitem_arr_tup(key_arrs, lo):
        luh__bgzp += 1
        while luh__bgzp < hi and getitem_arr_tup(key_arrs, luh__bgzp
            ) < getitem_arr_tup(key_arrs, luh__bgzp - 1):
            luh__bgzp += 1
        reverseRange(key_arrs, lo, luh__bgzp, data)
    else:
        luh__bgzp += 1
        while luh__bgzp < hi and getitem_arr_tup(key_arrs, luh__bgzp
            ) >= getitem_arr_tup(key_arrs, luh__bgzp - 1):
            luh__bgzp += 1
    return luh__bgzp - lo


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
    xhvq__qfmpk = 0
    while n >= MIN_MERGE:
        xhvq__qfmpk |= n & 1
        n >>= 1
    return n + xhvq__qfmpk


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    ihywq__wbvqo = len(key_arrs[0])
    tmpLength = (ihywq__wbvqo >> 1 if ihywq__wbvqo < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    avfp__ucnd = (5 if ihywq__wbvqo < 120 else 10 if ihywq__wbvqo < 1542 else
        19 if ihywq__wbvqo < 119151 else 40)
    runBase = np.empty(avfp__ucnd, np.int64)
    runLen = np.empty(avfp__ucnd, np.int64)
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
    wug__rtsso = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert wug__rtsso >= 0
    base1 += wug__rtsso
    len1 -= wug__rtsso
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
    eon__cnr = 0
    hymqg__wnkdh = 1
    if key > getitem_arr_tup(arr, base + hint):
        zem__oxyc = _len - hint
        while hymqg__wnkdh < zem__oxyc and key > getitem_arr_tup(arr, base +
            hint + hymqg__wnkdh):
            eon__cnr = hymqg__wnkdh
            hymqg__wnkdh = (hymqg__wnkdh << 1) + 1
            if hymqg__wnkdh <= 0:
                hymqg__wnkdh = zem__oxyc
        if hymqg__wnkdh > zem__oxyc:
            hymqg__wnkdh = zem__oxyc
        eon__cnr += hint
        hymqg__wnkdh += hint
    else:
        zem__oxyc = hint + 1
        while hymqg__wnkdh < zem__oxyc and key <= getitem_arr_tup(arr, base +
            hint - hymqg__wnkdh):
            eon__cnr = hymqg__wnkdh
            hymqg__wnkdh = (hymqg__wnkdh << 1) + 1
            if hymqg__wnkdh <= 0:
                hymqg__wnkdh = zem__oxyc
        if hymqg__wnkdh > zem__oxyc:
            hymqg__wnkdh = zem__oxyc
        tmp = eon__cnr
        eon__cnr = hint - hymqg__wnkdh
        hymqg__wnkdh = hint - tmp
    assert -1 <= eon__cnr and eon__cnr < hymqg__wnkdh and hymqg__wnkdh <= _len
    eon__cnr += 1
    while eon__cnr < hymqg__wnkdh:
        nsvcu__sskw = eon__cnr + (hymqg__wnkdh - eon__cnr >> 1)
        if key > getitem_arr_tup(arr, base + nsvcu__sskw):
            eon__cnr = nsvcu__sskw + 1
        else:
            hymqg__wnkdh = nsvcu__sskw
    assert eon__cnr == hymqg__wnkdh
    return hymqg__wnkdh


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    hymqg__wnkdh = 1
    eon__cnr = 0
    if key < getitem_arr_tup(arr, base + hint):
        zem__oxyc = hint + 1
        while hymqg__wnkdh < zem__oxyc and key < getitem_arr_tup(arr, base +
            hint - hymqg__wnkdh):
            eon__cnr = hymqg__wnkdh
            hymqg__wnkdh = (hymqg__wnkdh << 1) + 1
            if hymqg__wnkdh <= 0:
                hymqg__wnkdh = zem__oxyc
        if hymqg__wnkdh > zem__oxyc:
            hymqg__wnkdh = zem__oxyc
        tmp = eon__cnr
        eon__cnr = hint - hymqg__wnkdh
        hymqg__wnkdh = hint - tmp
    else:
        zem__oxyc = _len - hint
        while hymqg__wnkdh < zem__oxyc and key >= getitem_arr_tup(arr, base +
            hint + hymqg__wnkdh):
            eon__cnr = hymqg__wnkdh
            hymqg__wnkdh = (hymqg__wnkdh << 1) + 1
            if hymqg__wnkdh <= 0:
                hymqg__wnkdh = zem__oxyc
        if hymqg__wnkdh > zem__oxyc:
            hymqg__wnkdh = zem__oxyc
        eon__cnr += hint
        hymqg__wnkdh += hint
    assert -1 <= eon__cnr and eon__cnr < hymqg__wnkdh and hymqg__wnkdh <= _len
    eon__cnr += 1
    while eon__cnr < hymqg__wnkdh:
        nsvcu__sskw = eon__cnr + (hymqg__wnkdh - eon__cnr >> 1)
        if key < getitem_arr_tup(arr, base + nsvcu__sskw):
            hymqg__wnkdh = nsvcu__sskw
        else:
            eon__cnr = nsvcu__sskw + 1
    assert eon__cnr == hymqg__wnkdh
    return hymqg__wnkdh


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
        fwvq__dkaxs = 0
        msh__imwo = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                msh__imwo += 1
                fwvq__dkaxs = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                fwvq__dkaxs += 1
                msh__imwo = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not fwvq__dkaxs | msh__imwo < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            fwvq__dkaxs = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if fwvq__dkaxs != 0:
                copyRange_tup(tmp, cursor1, arr, dest, fwvq__dkaxs)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, fwvq__dkaxs)
                dest += fwvq__dkaxs
                cursor1 += fwvq__dkaxs
                len1 -= fwvq__dkaxs
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            msh__imwo = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if msh__imwo != 0:
                copyRange_tup(arr, cursor2, arr, dest, msh__imwo)
                copyRange_tup(arr_data, cursor2, arr_data, dest, msh__imwo)
                dest += msh__imwo
                cursor2 += msh__imwo
                len2 -= msh__imwo
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
            if not fwvq__dkaxs >= MIN_GALLOP | msh__imwo >= MIN_GALLOP:
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
        fwvq__dkaxs = 0
        msh__imwo = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                fwvq__dkaxs += 1
                msh__imwo = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                msh__imwo += 1
                fwvq__dkaxs = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not fwvq__dkaxs | msh__imwo < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            fwvq__dkaxs = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if fwvq__dkaxs != 0:
                dest -= fwvq__dkaxs
                cursor1 -= fwvq__dkaxs
                len1 -= fwvq__dkaxs
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, fwvq__dkaxs)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    fwvq__dkaxs)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            msh__imwo = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if msh__imwo != 0:
                dest -= msh__imwo
                cursor2 -= msh__imwo
                len2 -= msh__imwo
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, msh__imwo)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    msh__imwo)
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
            if not fwvq__dkaxs >= MIN_GALLOP | msh__imwo >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    nfzw__noq = len(key_arrs[0])
    if tmpLength < minCapacity:
        zhhbl__njw = minCapacity
        zhhbl__njw |= zhhbl__njw >> 1
        zhhbl__njw |= zhhbl__njw >> 2
        zhhbl__njw |= zhhbl__njw >> 4
        zhhbl__njw |= zhhbl__njw >> 8
        zhhbl__njw |= zhhbl__njw >> 16
        zhhbl__njw += 1
        if zhhbl__njw < 0:
            zhhbl__njw = minCapacity
        else:
            zhhbl__njw = min(zhhbl__njw, nfzw__noq >> 1)
        tmp = alloc_arr_tup(zhhbl__njw, key_arrs)
        tmp_data = alloc_arr_tup(zhhbl__njw, data)
        tmpLength = zhhbl__njw
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        ciqu__eew = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = ciqu__eew


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    cvx__vsls = arr_tup.count
    lxhef__xhui = 'def f(arr_tup, lo, hi):\n'
    for i in range(cvx__vsls):
        lxhef__xhui += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        lxhef__xhui += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        lxhef__xhui += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    lxhef__xhui += '  return\n'
    ytyj__izcrh = {}
    exec(lxhef__xhui, {}, ytyj__izcrh)
    qpv__mqftm = ytyj__izcrh['f']
    return qpv__mqftm


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    cvx__vsls = src_arr_tup.count
    assert cvx__vsls == dst_arr_tup.count
    lxhef__xhui = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(cvx__vsls):
        lxhef__xhui += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    lxhef__xhui += '  return\n'
    ytyj__izcrh = {}
    exec(lxhef__xhui, {'copyRange': copyRange}, ytyj__izcrh)
    pen__xrzqx = ytyj__izcrh['f']
    return pen__xrzqx


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    cvx__vsls = src_arr_tup.count
    assert cvx__vsls == dst_arr_tup.count
    lxhef__xhui = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(cvx__vsls):
        lxhef__xhui += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    lxhef__xhui += '  return\n'
    ytyj__izcrh = {}
    exec(lxhef__xhui, {'copyElement': copyElement}, ytyj__izcrh)
    pen__xrzqx = ytyj__izcrh['f']
    return pen__xrzqx


def getitem_arr_tup(arr_tup, ind):
    uuay__hnq = [arr[ind] for arr in arr_tup]
    return tuple(uuay__hnq)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    cvx__vsls = arr_tup.count
    lxhef__xhui = 'def f(arr_tup, ind):\n'
    lxhef__xhui += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(cvx__vsls)]), ',' if cvx__vsls == 1 else '')
    ytyj__izcrh = {}
    exec(lxhef__xhui, {}, ytyj__izcrh)
    sor__xom = ytyj__izcrh['f']
    return sor__xom


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, jiyp__pkoq in zip(arr_tup, val_tup):
        arr[ind] = jiyp__pkoq


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    cvx__vsls = arr_tup.count
    lxhef__xhui = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(cvx__vsls):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            lxhef__xhui += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            lxhef__xhui += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    lxhef__xhui += '  return\n'
    ytyj__izcrh = {}
    exec(lxhef__xhui, {}, ytyj__izcrh)
    sor__xom = ytyj__izcrh['f']
    return sor__xom


def test():
    import time
    izncc__vxn = time.time()
    ueqa__apf = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((ueqa__apf,), 0, 3, data)
    print('compile time', time.time() - izncc__vxn)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    rbewv__oagco = np.random.ranf(n)
    zzvj__tjk = pd.DataFrame({'A': rbewv__oagco, 'B': data[0], 'C': data[1]})
    izncc__vxn = time.time()
    zlk__rld = zzvj__tjk.sort_values('A', inplace=False)
    qlebx__unvvb = time.time()
    sort((rbewv__oagco,), 0, n, data)
    print('Bodo', time.time() - qlebx__unvvb, 'Numpy', qlebx__unvvb -
        izncc__vxn)
    np.testing.assert_almost_equal(data[0], zlk__rld.B.values)
    np.testing.assert_almost_equal(data[1], zlk__rld.C.values)


if __name__ == '__main__':
    test()
