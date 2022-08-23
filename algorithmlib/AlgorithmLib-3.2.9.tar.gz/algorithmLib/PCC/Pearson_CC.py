# -*- coding: UTF-8 -*-
import sys
sys.path.append('../')
from ctypes import *
import ctypes
import numpy as np
#  * -------------------------------------------------------------------------
#  * Arguments    : const emxArray_real_T *ref_in
#  *                const emxArray_real_T *sig_in
#  *                double fs
#  *                double *delay
#  *                double *err
#  * Return Type  : void
#  */
# void delay_estimation_15s(const emxArray_real_T *ref_in, const emxArray_real_T
#   *sig_in, double fs, double *delay, double *err)

def cal_PCC(refData, testData,calSize,mydll):
    """
    """

    refstruct = refData.ctypes.data_as(POINTER(c_double))
    teststruct = testData.ctypes.data_as(POINTER(c_double))
    pcc= c_double(0.0)
    mydll.Pearson_Correlation(refstruct,teststruct,c_long(calSize),byref(pcc))
    return pcc.value


if __name__ == '__main__':
    ref = r'C:\Users\vcloud_avl\Documents\我的POPO\src.wav'
    test = r'C:\Users\vcloud_avl\Documents\我的POPO\test.wav'
    from commFunction import  get_data_array
    import platform,time
    newdata,fs,ch = get_data_array(ref)
    refdata,fs,ch = get_data_array(test)
    newdata = newdata[:10000].astype(np.double)
    refdata = refdata[:10000].astype(np.double)
    mydll = None
    cur_paltform = platform.platform().split('-')[0]
    if cur_paltform == 'Windows':
        mydll = ctypes.windll.LoadLibrary(sys.prefix + '/pcc.dll')
    if cur_paltform == 'macOS':
        mydll = CDLL(sys.prefix + '/pcc.dylib')
    mydll.Pearson_Correlation.argtypes = [POINTER(c_double), POINTER(c_double), c_long, POINTER(c_double)]
    # newdata = np.arange(0,20000,2)
    # refdata = np.arange(10000,30000,2)
    # print(len(newdata),len(refdata))
    # print(time.time())
    # print(np.corrcoef(refdata,newdata))
    # print(time.time())
    # print(cal_PCC(refdata,newdata,10000,mydll))
    # print(time.time())
    suma,sumb = 0,0
    for e in range(10000):
        a = time.time()
        np.corrcoef(refdata, newdata)
        b = time.time()
        suma += b - a
        c = time.time()
        cal_PCC(refdata, newdata, 10000, mydll)
        d = time.time()
        sumb += d - c
    print(suma/10000)
    print(sumb/10000)
    pass