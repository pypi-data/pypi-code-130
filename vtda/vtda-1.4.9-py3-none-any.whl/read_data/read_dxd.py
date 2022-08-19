# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 14:47:25 2021

@author: Administrator
"""

from ctypes import *
from enum import Enum
import sys
import _ctypes
import pandas as pd
import numpy as np
import datetime

INT_SIZE = 4 # size of integer
DOUBLE_SIZE = 8 # size of double

class DWStatus(Enum):
    DWSTAT_OK = 0
    DWSTAT_ERROR = 1
    DWSTAT_ERROR_FILE_CANNOT_OPEN = 2
    DWSTAT_ERROR_FILE_ALREADY_IN_USE = 3
    DWSTAT_ERROR_FILE_CORRUPT = 4
    DWSTAT_ERROR_NO_MEMORY_ALLOC = 5
    DWSTAT_ERROR_CREATE_DEST_FILE = 6
    DWSTAT_ERROR_EXTRACTING_FILE = 7
    DWSTAT_ERROR_CANNOT_OPEN_EXTRACTED_FILE = 8

class DWChannelProps(Enum):
    DW_DATA_TYPE = 0
    DW_DATA_TYPE_LEN_BYTES = 1
    DW_CH_INDEX = 2
    DW_CH_INDEX_LEN = 3
    DW_CH_TYPE = 4
    DW_CH_SCALE = 5
    DW_CH_OFFSET = 6
    DW_CH_XML = 7
    DW_CH_XML_LEN = 8
    DW_CH_XMLPROPS = 9
    DW_CH_XMLPROPS_LEN = 10

class DWChannelType(Enum):
    DW_CH_TYPE_SYNC = 0 # sync
    DW_CH_TYPE_ASYNC = 1 # async
    DW_CH_TYPE_SV = 2 # single value

class DWFileInfo(Structure):
    _pack_ = 1
    _fields_ =\
    [
        ("sample_rate", c_double),
        ("start_store_time", c_double),
        ("duration", c_double)
    ]

class DWChannel(Structure):
    _pack_ = 1
    _fields_ =\
    [
        ("index", c_int),
        ("name", c_char * 100),
        ("unit", c_char * 20),
        ("description", c_char * 200),
        ("color", c_uint),
        ("array_size", c_int),
        ("data_type", c_int)
    ]

class DWEvent(Structure):
    _pack_ = 1
    _fields_ =\
    [
        ("event_type", c_int),
        ("time_stamp", c_double),
        ("event_text", c_char * 200)
    ]

class DWReducedValue(Structure):
    _pack_ = 1
    _fields_ =\
    [
        ("time_stamp", c_double),
        ("ave", c_double),
        ("min", c_double),
        ("max", c_double),
        ("rms", c_double)
    ]
    
class DWArrayInfo(Structure):
    _pack_ = 1
    _fields_ =\
    [
        ("index", c_int),
        ("name", c_char * 100),
        ("unit", c_char * 20),
        ("size", c_int)
    ]

class DWCANPortData(Structure):
    _pack_ = 1
    _fields_ =\
    [
        ("arb_id", c_ulong),
        ("data", c_char * 8)
    ]

class DWComplex(Structure):
    _pack_ = 1
    _fields_ =\
    [
        ("re", c_double),
        ("im", c_double)
    ]

class DWEventType(Enum):
    etStart = 1
    etStop = 2
    etTrigger = 3
    etVStart = 11
    etVStop = 12
    etKeyboard = 20
    etNotice = 21
    etVoice = 22
    etModule = 24

class DWStoreType(Enum):
    ST_ALWAYS_FAST = 0
    ST_ALWAYS_SLOW = 1
    ST_FAST_ON_TRIGGER = 2
    ST_FAST_ON_TRIGGER_SLOW_OTH = 3

class DWDataType(Enum):
    dtByte = 0
    dtShortInt = 1
    dtSmallInt = 2
    dtWord = 3
    dtInteger = 4
    dtSingle = 5
    dtInt64 = 6
    dtDouble = 7
    dtLongword = 8
    dtComplexSingle = 9
    dtComplexDouble = 10
    dtText = 11
    dtBinary = 12
    dtCANPortData = 13
    dtCANFDPortData = 14
    dtBytes8 = 15
    dtBytes16 = 16
    dtBytes32 = 17
    dtBytes64 = 18

def DWRaiseError(err_str):
    print(err_str)
    #sys.exit(-1)

dir_='E:/20200620磁各庄实验室/6科研/平稳性/dewesoft_to_dasp/DWDataReader/DWDataReader_v4_2_0_20/Win32&64 Python'
name='北京地铁8号线车辆平稳性测试_2021_11_20_上行.dxd'
dll_name='DWDataReaderLib64.dll'
dllname = dir_+'/'+dll_name
lib = cdll.LoadLibrary(dllname)
#dllname.decode('utf-8').encode('gbk')


# init data reader
if lib.DWInit() != DWStatus.DWSTAT_OK.value:
    DWRaiseError("DWDataReader: DWInit() failed")

# get data reader version
print("DWDataReader version: " + str(lib.DWGetVersion()))

# add additional data reader
if lib.DWAddReader() != DWStatus.DWSTAT_OK.value:
    DWRaiseError("DWDataReader: DWAddReader() failed")

# get number of open data readers
num = c_int()
if lib.DWGetNumReaders(byref(num)) != DWStatus.DWSTAT_OK.value:
    DWRaiseError("DWDataReader: DWGetNumReaders() failed")
print("Number of data readers: " + str(num.value))

# open data file
# data file must be in the same folder as the python script
#str = input('Please enter a data file name (.d7d, .d7z or .dxd):')

import os
os.chdir(dir_)

file_name = c_char_p(name.encode("GBK"))
file_info = DWFileInfo(0, 0, 0)
if lib.DWOpenDataFile(file_name, c_void_p(addressof(file_info))) != DWStatus.DWSTAT_OK.value:
    DWRaiseError("DWDataReader: DWOpenDataFile() failed")
print("Sample rate: %.2f" %  file_info.sample_rate)
print("Start store time: %.2f" % file_info.start_store_time)
print("Duration: %.2f" % file_info.duration)


# get num channels
num = lib.DWGetChannelListCount()
if num == -1:
    DWRaiseError("DWDataReader: DWGetChannelListCount() failed")
print("Number of channels: %d" % num)

# get channel list
ch_list = (DWChannel * num)()
if lib.DWGetChannelList(byref(ch_list)) != DWStatus.DWSTAT_OK.value:
    DWRaiseError("DWDataReader: DWGetChannelList() failed")

print("\n")

#----------------------------------------------------------------------------------------------------------------
# channel loop
#----------------------------------------------------------------------------------------------------------------
for i in range(0, num):
    pass
    # basic channel properties
    print("************************************************")
    print("Channel #%d" % i)
    print("************************************************")
    print("Index: %d" % ch_list[i].index)
    print("Name: %s" % ch_list[i].name.decode('utf-8'))
    print("Unit: %s" % ch_list[i].unit)
    print("Description: %s" % ch_list[i].description.decode('utf-8'))

    # channel factors
    idx = c_int(i)
    ch_scale = c_double()
    ch_offset = c_double()
    if lib.DWGetChannelFactors(idx, byref(ch_scale), byref(ch_offset)) != DWStatus.DWSTAT_OK.value:
        DWRaiseError("DWDataReader: DWGetChannelFactors() failed")

    print("Scale: %.2f" % ch_scale.value)
    print("Offset: %.2f" % ch_offset.value)

    # channel type
    max_len = c_int(INT_SIZE)
    buff = create_string_buffer(max_len.value)
    p_buff = cast(buff, POINTER(c_void_p))
    if lib.DWGetChannelProps(idx, c_int(DWChannelProps.DW_CH_TYPE.value), p_buff, byref(max_len)) != DWStatus.DWSTAT_OK.value:
        DWRaiseError("DWDataReader: DWGetChannelProps() failed")
    ch_type = cast(p_buff, POINTER(c_int)).contents

    if ch_type.value == DWChannelType.DW_CH_TYPE_SYNC.value:
        print("Channel type: sync")
    elif ch_type.value == DWChannelType.DW_CH_TYPE_ASYNC.value:
        print("Channel type: async")
    elif ch_type.value == DWChannelType.DW_CH_TYPE_SV.value:
        print("Channel type: single value")
    else:
        print("Channel type: unknown")

    # channel data type
    if lib.DWGetChannelProps(idx, c_int(DWChannelProps.DW_DATA_TYPE.value), p_buff, byref(max_len)) != DWStatus.DWSTAT_OK.value:
        DWRaiseError("DWDataReader: DWGetChannelProps() failed")
    data_type = cast(p_buff, POINTER(c_int)).contents
    print("Data type: %s" % DWDataType(data_type.value).name)

    # number of samples
    dw_ch_index = c_int(ch_list[i].index)
    sample_cnt = c_int()
    sample_cnt = lib.DWGetScaledSamplesCount(dw_ch_index)
    if sample_cnt < 0:
        DWRaiseError("DWDataReader: DWGetScaledSamplesCount() failed")
    print("Num. samples: %d" % sample_cnt)

    # get actual data
    data = create_string_buffer(DOUBLE_SIZE * sample_cnt * ch_list[i].array_size)
    time_stamp = create_string_buffer(DOUBLE_SIZE * sample_cnt)
    p_data = cast(data, POINTER(c_double))
    p_time_stamp = cast(time_stamp, POINTER(c_double))
    if lib.DWGetScaledSamples(dw_ch_index, c_int64(0), sample_cnt, p_data, p_time_stamp) != DWStatus.DWSTAT_OK.value:
        DWRaiseError("DWDataReader: DWGetScaledSamples() failed")

    # diplay data
    print("Data:")
    for j in range(0, sample_cnt):
        for k in range(0, ch_list[i].array_size):
            print("  Time: %.6f   Value=%.2f" % (p_time_stamp[j], p_data[j * ch_list[i].array_size + k]))

    print("\n")
#----------------------------------------------------------------------------------------------------------------
# end channel loop
#----------------------------------------------------------------------------------------------------------------

# close data file
if lib.DWCloseDataFile() != DWStatus.DWSTAT_OK.value:
    DWRaiseError("DWDataReader: DWCloseDataFile() failed")

# deinit
if lib.DWDeInit() != DWStatus.DWSTAT_OK.value:
    DWRaiseError("DWDataReader: DWDeInit() failed")

# close DLL
_ctypes.FreeLibrary(lib._handle)
del lib
