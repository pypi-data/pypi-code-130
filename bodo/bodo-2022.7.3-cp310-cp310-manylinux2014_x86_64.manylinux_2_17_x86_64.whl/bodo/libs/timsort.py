import numpy as np
import pandas as pd
import numba
from numba.extending import overload
from bodo.utils.utils import alloc_arr_tup
MIN_MERGE = 32


@numba.njit(no_cpython_wrapper=True, cache=True)
def sort(key_arrs, lo, hi, data):
    gss__ykd = hi - lo
    if gss__ykd < 2:
        return
    if gss__ykd < MIN_MERGE:
        mgy__qjzqa = countRunAndMakeAscending(key_arrs, lo, hi, data)
        binarySort(key_arrs, lo, hi, lo + mgy__qjzqa, data)
        return
    stackSize, runBase, runLen, tmpLength, tmp, tmp_data, minGallop = (
        init_sort_start(key_arrs, data))
    fmjvt__flxo = minRunLength(gss__ykd)
    while True:
        qtz__uvpr = countRunAndMakeAscending(key_arrs, lo, hi, data)
        if qtz__uvpr < fmjvt__flxo:
            tnmqi__apxv = gss__ykd if gss__ykd <= fmjvt__flxo else fmjvt__flxo
            binarySort(key_arrs, lo, lo + tnmqi__apxv, lo + qtz__uvpr, data)
            qtz__uvpr = tnmqi__apxv
        stackSize = pushRun(stackSize, runBase, runLen, lo, qtz__uvpr)
        stackSize, tmpLength, tmp, tmp_data, minGallop = mergeCollapse(
            stackSize, runBase, runLen, key_arrs, data, tmpLength, tmp,
            tmp_data, minGallop)
        lo += qtz__uvpr
        gss__ykd -= qtz__uvpr
        if gss__ykd == 0:
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
        umg__pjxvo = getitem_arr_tup(key_arrs, start)
        bshmw__yfcmw = getitem_arr_tup(data, start)
        ids__aaxjv = lo
        mftd__fcpq = start
        assert ids__aaxjv <= mftd__fcpq
        while ids__aaxjv < mftd__fcpq:
            yskz__kyvbd = ids__aaxjv + mftd__fcpq >> 1
            if umg__pjxvo < getitem_arr_tup(key_arrs, yskz__kyvbd):
                mftd__fcpq = yskz__kyvbd
            else:
                ids__aaxjv = yskz__kyvbd + 1
        assert ids__aaxjv == mftd__fcpq
        n = start - ids__aaxjv
        copyRange_tup(key_arrs, ids__aaxjv, key_arrs, ids__aaxjv + 1, n)
        copyRange_tup(data, ids__aaxjv, data, ids__aaxjv + 1, n)
        setitem_arr_tup(key_arrs, ids__aaxjv, umg__pjxvo)
        setitem_arr_tup(data, ids__aaxjv, bshmw__yfcmw)
        start += 1


@numba.njit(no_cpython_wrapper=True, cache=True)
def countRunAndMakeAscending(key_arrs, lo, hi, data):
    assert lo < hi
    rsjcw__gejz = lo + 1
    if rsjcw__gejz == hi:
        return 1
    if getitem_arr_tup(key_arrs, rsjcw__gejz) < getitem_arr_tup(key_arrs, lo):
        rsjcw__gejz += 1
        while rsjcw__gejz < hi and getitem_arr_tup(key_arrs, rsjcw__gejz
            ) < getitem_arr_tup(key_arrs, rsjcw__gejz - 1):
            rsjcw__gejz += 1
        reverseRange(key_arrs, lo, rsjcw__gejz, data)
    else:
        rsjcw__gejz += 1
        while rsjcw__gejz < hi and getitem_arr_tup(key_arrs, rsjcw__gejz
            ) >= getitem_arr_tup(key_arrs, rsjcw__gejz - 1):
            rsjcw__gejz += 1
    return rsjcw__gejz - lo


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
    ddbp__mqj = 0
    while n >= MIN_MERGE:
        ddbp__mqj |= n & 1
        n >>= 1
    return n + ddbp__mqj


MIN_GALLOP = 7
INITIAL_TMP_STORAGE_LENGTH = 256


@numba.njit(no_cpython_wrapper=True, cache=True)
def init_sort_start(key_arrs, data):
    minGallop = MIN_GALLOP
    nyk__ziger = len(key_arrs[0])
    tmpLength = (nyk__ziger >> 1 if nyk__ziger < 2 *
        INITIAL_TMP_STORAGE_LENGTH else INITIAL_TMP_STORAGE_LENGTH)
    tmp = alloc_arr_tup(tmpLength, key_arrs)
    tmp_data = alloc_arr_tup(tmpLength, data)
    stackSize = 0
    ngpl__box = (5 if nyk__ziger < 120 else 10 if nyk__ziger < 1542 else 19 if
        nyk__ziger < 119151 else 40)
    runBase = np.empty(ngpl__box, np.int64)
    runLen = np.empty(ngpl__box, np.int64)
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
    tmo__lrm = gallopRight(getitem_arr_tup(key_arrs, base2), key_arrs,
        base1, len1, 0)
    assert tmo__lrm >= 0
    base1 += tmo__lrm
    len1 -= tmo__lrm
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
    cpz__aalb = 0
    tkl__uajtn = 1
    if key > getitem_arr_tup(arr, base + hint):
        jjx__smncg = _len - hint
        while tkl__uajtn < jjx__smncg and key > getitem_arr_tup(arr, base +
            hint + tkl__uajtn):
            cpz__aalb = tkl__uajtn
            tkl__uajtn = (tkl__uajtn << 1) + 1
            if tkl__uajtn <= 0:
                tkl__uajtn = jjx__smncg
        if tkl__uajtn > jjx__smncg:
            tkl__uajtn = jjx__smncg
        cpz__aalb += hint
        tkl__uajtn += hint
    else:
        jjx__smncg = hint + 1
        while tkl__uajtn < jjx__smncg and key <= getitem_arr_tup(arr, base +
            hint - tkl__uajtn):
            cpz__aalb = tkl__uajtn
            tkl__uajtn = (tkl__uajtn << 1) + 1
            if tkl__uajtn <= 0:
                tkl__uajtn = jjx__smncg
        if tkl__uajtn > jjx__smncg:
            tkl__uajtn = jjx__smncg
        tmp = cpz__aalb
        cpz__aalb = hint - tkl__uajtn
        tkl__uajtn = hint - tmp
    assert -1 <= cpz__aalb and cpz__aalb < tkl__uajtn and tkl__uajtn <= _len
    cpz__aalb += 1
    while cpz__aalb < tkl__uajtn:
        pjac__tjhmw = cpz__aalb + (tkl__uajtn - cpz__aalb >> 1)
        if key > getitem_arr_tup(arr, base + pjac__tjhmw):
            cpz__aalb = pjac__tjhmw + 1
        else:
            tkl__uajtn = pjac__tjhmw
    assert cpz__aalb == tkl__uajtn
    return tkl__uajtn


@numba.njit(no_cpython_wrapper=True, cache=True)
def gallopRight(key, arr, base, _len, hint):
    assert _len > 0 and hint >= 0 and hint < _len
    tkl__uajtn = 1
    cpz__aalb = 0
    if key < getitem_arr_tup(arr, base + hint):
        jjx__smncg = hint + 1
        while tkl__uajtn < jjx__smncg and key < getitem_arr_tup(arr, base +
            hint - tkl__uajtn):
            cpz__aalb = tkl__uajtn
            tkl__uajtn = (tkl__uajtn << 1) + 1
            if tkl__uajtn <= 0:
                tkl__uajtn = jjx__smncg
        if tkl__uajtn > jjx__smncg:
            tkl__uajtn = jjx__smncg
        tmp = cpz__aalb
        cpz__aalb = hint - tkl__uajtn
        tkl__uajtn = hint - tmp
    else:
        jjx__smncg = _len - hint
        while tkl__uajtn < jjx__smncg and key >= getitem_arr_tup(arr, base +
            hint + tkl__uajtn):
            cpz__aalb = tkl__uajtn
            tkl__uajtn = (tkl__uajtn << 1) + 1
            if tkl__uajtn <= 0:
                tkl__uajtn = jjx__smncg
        if tkl__uajtn > jjx__smncg:
            tkl__uajtn = jjx__smncg
        cpz__aalb += hint
        tkl__uajtn += hint
    assert -1 <= cpz__aalb and cpz__aalb < tkl__uajtn and tkl__uajtn <= _len
    cpz__aalb += 1
    while cpz__aalb < tkl__uajtn:
        pjac__tjhmw = cpz__aalb + (tkl__uajtn - cpz__aalb >> 1)
        if key < getitem_arr_tup(arr, base + pjac__tjhmw):
            tkl__uajtn = pjac__tjhmw
        else:
            cpz__aalb = pjac__tjhmw + 1
    assert cpz__aalb == tkl__uajtn
    return tkl__uajtn


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
        zwfme__xrfbk = 0
        sekx__edfi = 0
        while True:
            assert len1 > 1 and len2 > 0
            if getitem_arr_tup(arr, cursor2) < getitem_arr_tup(tmp, cursor1):
                copyElement_tup(arr, cursor2, arr, dest)
                copyElement_tup(arr_data, cursor2, arr_data, dest)
                cursor2 += 1
                dest += 1
                sekx__edfi += 1
                zwfme__xrfbk = 0
                len2 -= 1
                if len2 == 0:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor1, arr, dest)
                copyElement_tup(tmp_data, cursor1, arr_data, dest)
                cursor1 += 1
                dest += 1
                zwfme__xrfbk += 1
                sekx__edfi = 0
                len1 -= 1
                if len1 == 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            if not zwfme__xrfbk | sekx__edfi < minGallop:
                break
        while True:
            assert len1 > 1 and len2 > 0
            zwfme__xrfbk = gallopRight(getitem_arr_tup(arr, cursor2), tmp,
                cursor1, len1, 0)
            if zwfme__xrfbk != 0:
                copyRange_tup(tmp, cursor1, arr, dest, zwfme__xrfbk)
                copyRange_tup(tmp_data, cursor1, arr_data, dest, zwfme__xrfbk)
                dest += zwfme__xrfbk
                cursor1 += zwfme__xrfbk
                len1 -= zwfme__xrfbk
                if len1 <= 1:
                    return len1, len2, cursor1, cursor2, dest, minGallop
            copyElement_tup(arr, cursor2, arr, dest)
            copyElement_tup(arr_data, cursor2, arr_data, dest)
            cursor2 += 1
            dest += 1
            len2 -= 1
            if len2 == 0:
                return len1, len2, cursor1, cursor2, dest, minGallop
            sekx__edfi = gallopLeft(getitem_arr_tup(tmp, cursor1), arr,
                cursor2, len2, 0)
            if sekx__edfi != 0:
                copyRange_tup(arr, cursor2, arr, dest, sekx__edfi)
                copyRange_tup(arr_data, cursor2, arr_data, dest, sekx__edfi)
                dest += sekx__edfi
                cursor2 += sekx__edfi
                len2 -= sekx__edfi
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
            if not zwfme__xrfbk >= MIN_GALLOP | sekx__edfi >= MIN_GALLOP:
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
        zwfme__xrfbk = 0
        sekx__edfi = 0
        while True:
            assert len1 > 0 and len2 > 1
            if getitem_arr_tup(tmp, cursor2) < getitem_arr_tup(arr, cursor1):
                copyElement_tup(arr, cursor1, arr, dest)
                copyElement_tup(arr_data, cursor1, arr_data, dest)
                cursor1 -= 1
                dest -= 1
                zwfme__xrfbk += 1
                sekx__edfi = 0
                len1 -= 1
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            else:
                copyElement_tup(tmp, cursor2, arr, dest)
                copyElement_tup(tmp_data, cursor2, arr_data, dest)
                cursor2 -= 1
                dest -= 1
                sekx__edfi += 1
                zwfme__xrfbk = 0
                len2 -= 1
                if len2 == 1:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            if not zwfme__xrfbk | sekx__edfi < minGallop:
                break
        while True:
            assert len1 > 0 and len2 > 1
            zwfme__xrfbk = len1 - gallopRight(getitem_arr_tup(tmp, cursor2),
                arr, base1, len1, len1 - 1)
            if zwfme__xrfbk != 0:
                dest -= zwfme__xrfbk
                cursor1 -= zwfme__xrfbk
                len1 -= zwfme__xrfbk
                copyRange_tup(arr, cursor1 + 1, arr, dest + 1, zwfme__xrfbk)
                copyRange_tup(arr_data, cursor1 + 1, arr_data, dest + 1,
                    zwfme__xrfbk)
                if len1 == 0:
                    return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            copyElement_tup(tmp, cursor2, arr, dest)
            copyElement_tup(tmp_data, cursor2, arr_data, dest)
            cursor2 -= 1
            dest -= 1
            len2 -= 1
            if len2 == 1:
                return len1, len2, tmp, cursor1, cursor2, dest, minGallop
            sekx__edfi = len2 - gallopLeft(getitem_arr_tup(arr, cursor1),
                tmp, 0, len2, len2 - 1)
            if sekx__edfi != 0:
                dest -= sekx__edfi
                cursor2 -= sekx__edfi
                len2 -= sekx__edfi
                copyRange_tup(tmp, cursor2 + 1, arr, dest + 1, sekx__edfi)
                copyRange_tup(tmp_data, cursor2 + 1, arr_data, dest + 1,
                    sekx__edfi)
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
            if not zwfme__xrfbk >= MIN_GALLOP | sekx__edfi >= MIN_GALLOP:
                break
        if minGallop < 0:
            minGallop = 0
        minGallop += 2
    return len1, len2, tmp, cursor1, cursor2, dest, minGallop


@numba.njit(no_cpython_wrapper=True, cache=True)
def ensureCapacity(tmpLength, tmp, tmp_data, key_arrs, data, minCapacity):
    vyhsh__asr = len(key_arrs[0])
    if tmpLength < minCapacity:
        kbu__gwov = minCapacity
        kbu__gwov |= kbu__gwov >> 1
        kbu__gwov |= kbu__gwov >> 2
        kbu__gwov |= kbu__gwov >> 4
        kbu__gwov |= kbu__gwov >> 8
        kbu__gwov |= kbu__gwov >> 16
        kbu__gwov += 1
        if kbu__gwov < 0:
            kbu__gwov = minCapacity
        else:
            kbu__gwov = min(kbu__gwov, vyhsh__asr >> 1)
        tmp = alloc_arr_tup(kbu__gwov, key_arrs)
        tmp_data = alloc_arr_tup(kbu__gwov, data)
        tmpLength = kbu__gwov
    return tmpLength, tmp, tmp_data


def swap_arrs(data, lo, hi):
    for arr in data:
        qbei__jnvby = arr[lo]
        arr[lo] = arr[hi]
        arr[hi] = qbei__jnvby


@overload(swap_arrs, no_unliteral=True)
def swap_arrs_overload(arr_tup, lo, hi):
    rsy__ivu = arr_tup.count
    freuy__aizw = 'def f(arr_tup, lo, hi):\n'
    for i in range(rsy__ivu):
        freuy__aizw += '  tmp_v_{} = arr_tup[{}][lo]\n'.format(i, i)
        freuy__aizw += '  arr_tup[{}][lo] = arr_tup[{}][hi]\n'.format(i, i)
        freuy__aizw += '  arr_tup[{}][hi] = tmp_v_{}\n'.format(i, i)
    freuy__aizw += '  return\n'
    ymez__shkpv = {}
    exec(freuy__aizw, {}, ymez__shkpv)
    pguf__fvara = ymez__shkpv['f']
    return pguf__fvara


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyRange(src_arr, src_pos, dst_arr, dst_pos, n):
    dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


def copyRange_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos:dst_pos + n] = src_arr[src_pos:src_pos + n]


@overload(copyRange_tup, no_unliteral=True)
def copyRange_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):
    rsy__ivu = src_arr_tup.count
    assert rsy__ivu == dst_arr_tup.count
    freuy__aizw = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos, n):\n'
    for i in range(rsy__ivu):
        freuy__aizw += (
            '  copyRange(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos, n)\n'
            .format(i, i))
    freuy__aizw += '  return\n'
    ymez__shkpv = {}
    exec(freuy__aizw, {'copyRange': copyRange}, ymez__shkpv)
    lkuq__yvm = ymez__shkpv['f']
    return lkuq__yvm


@numba.njit(no_cpython_wrapper=True, cache=True)
def copyElement(src_arr, src_pos, dst_arr, dst_pos):
    dst_arr[dst_pos] = src_arr[src_pos]


def copyElement_tup(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    for src_arr, dst_arr in zip(src_arr_tup, dst_arr_tup):
        dst_arr[dst_pos] = src_arr[src_pos]


@overload(copyElement_tup, no_unliteral=True)
def copyElement_tup_overload(src_arr_tup, src_pos, dst_arr_tup, dst_pos):
    rsy__ivu = src_arr_tup.count
    assert rsy__ivu == dst_arr_tup.count
    freuy__aizw = 'def f(src_arr_tup, src_pos, dst_arr_tup, dst_pos):\n'
    for i in range(rsy__ivu):
        freuy__aizw += (
            '  copyElement(src_arr_tup[{}], src_pos, dst_arr_tup[{}], dst_pos)\n'
            .format(i, i))
    freuy__aizw += '  return\n'
    ymez__shkpv = {}
    exec(freuy__aizw, {'copyElement': copyElement}, ymez__shkpv)
    lkuq__yvm = ymez__shkpv['f']
    return lkuq__yvm


def getitem_arr_tup(arr_tup, ind):
    wxckq__afyyn = [arr[ind] for arr in arr_tup]
    return tuple(wxckq__afyyn)


@overload(getitem_arr_tup, no_unliteral=True)
def getitem_arr_tup_overload(arr_tup, ind):
    rsy__ivu = arr_tup.count
    freuy__aizw = 'def f(arr_tup, ind):\n'
    freuy__aizw += '  return ({}{})\n'.format(','.join(['arr_tup[{}][ind]'.
        format(i) for i in range(rsy__ivu)]), ',' if rsy__ivu == 1 else '')
    ymez__shkpv = {}
    exec(freuy__aizw, {}, ymez__shkpv)
    cqr__cfrr = ymez__shkpv['f']
    return cqr__cfrr


def setitem_arr_tup(arr_tup, ind, val_tup):
    for arr, xpzq__xwyn in zip(arr_tup, val_tup):
        arr[ind] = xpzq__xwyn


@overload(setitem_arr_tup, no_unliteral=True)
def setitem_arr_tup_overload(arr_tup, ind, val_tup):
    rsy__ivu = arr_tup.count
    freuy__aizw = 'def f(arr_tup, ind, val_tup):\n'
    for i in range(rsy__ivu):
        if isinstance(val_tup, numba.core.types.BaseTuple):
            freuy__aizw += '  arr_tup[{}][ind] = val_tup[{}]\n'.format(i, i)
        else:
            assert arr_tup.count == 1
            freuy__aizw += '  arr_tup[{}][ind] = val_tup\n'.format(i)
    freuy__aizw += '  return\n'
    ymez__shkpv = {}
    exec(freuy__aizw, {}, ymez__shkpv)
    cqr__cfrr = ymez__shkpv['f']
    return cqr__cfrr


def test():
    import time
    qoule__ejvfv = time.time()
    gyqjt__qfr = np.ones(3)
    data = np.arange(3), np.ones(3)
    sort((gyqjt__qfr,), 0, 3, data)
    print('compile time', time.time() - qoule__ejvfv)
    n = 210000
    np.random.seed(2)
    data = np.arange(n), np.random.ranf(n)
    jhea__xlwz = np.random.ranf(n)
    qpenj__tspom = pd.DataFrame({'A': jhea__xlwz, 'B': data[0], 'C': data[1]})
    qoule__ejvfv = time.time()
    hxso__bjl = qpenj__tspom.sort_values('A', inplace=False)
    yeh__fla = time.time()
    sort((jhea__xlwz,), 0, n, data)
    print('Bodo', time.time() - yeh__fla, 'Numpy', yeh__fla - qoule__ejvfv)
    np.testing.assert_almost_equal(data[0], hxso__bjl.B.values)
    np.testing.assert_almost_equal(data[1], hxso__bjl.C.values)


if __name__ == '__main__':
    test()
