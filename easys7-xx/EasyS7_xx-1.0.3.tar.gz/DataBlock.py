#-*- coding: utf-8 -*
from re import I
import snap7
import random
import sys
from datetime import datetime
from enum import Enum
from EasyS7.Utility import *
from EasyS7.DataTypes.DTdint import  DTdint
from EasyS7.DataTypes.DTbool import  DTbool
from EasyS7.DataTypes.DTtime import  DTtime
from EasyS7.DataTypes.DTint import  DTint
from EasyS7.DataTypes.DTUint import  DTUint
from EasyS7.DataTypes.DTstring import  DTstring
from decimal import Decimal as D

class Areas(Enum):
    Input = 1
    Output = 2
    Merker = 3
    DB = 4
    Counter = 5
    Timer = 6

class DataTypes(Enum):
    Real = 1
    Bool = 2
    DInt = 3
    UDInt = 4
    Int = 5
    DTime = 6
    String = 7
    Multiple = 8
    UInt = 9
    SInt = 10


class DataBlockObj(object):
		pass




#data block reading
def dbRead(plc,db_num,length,dbitems):

    data=plc.db_read(db_num,0,length)
    obj = DataBlockObj()

    for item in dbitems:
        value = (None,item['name'])
        offset = int(item['bytebit'].split('.')[0])

        if item['datatype']=='Real':
            value = (snap7.util.get_real(data,offset),item['name'].replace(" ","_").replace("/","_"))
            obj.__setattr__(item['name'].replace(" ","_").replace("/","_"), value[0])

        if item['datatype']=='Bool':
            bit =int(item['bytebit'].split('.')[1])
            value = snap7.util.get_bool(data, offset, bit)
            obj.__setattr__(item['name'].replace(" ","_").replace("/","_"), value)

        if item['datatype']=='DInt':

            value = snap7.util.get_dint(data, offset)
            obj.__setattr__(item['name'].replace(" ","_").replace("/","_"), value)

        if item['datatype']=='UDInt':

            value = snap7.util.get_udint(data, offset)
            obj.__setattr__(item['name'].replace(" ","_").replace("/","_"), value)

        if item['datatype']=='Int':

            value = snap7.util.get_int(data, offset)
            obj.__setattr__(item['name'].replace(" ","_").replace("/","_"), value)

        if item['datatype']=='UInt':

            value = snap7.util.get_uint(data, offset)
            obj.__setattr__(item['name'].replace(" ","_").replace("/","_"), value)

        if item['datatype']=='Time':
            value = snap7.util.get_time(data, offset)
            obj.__setattr__(item['name'].replace(" ","_").replace("/","_"), value)

        if item['datatype'] == 'SInt':
            value = snap7.util.get_sint(data, offset)
            obj.__setattr__(item['name'].replace(" ","_").replace("/","_"), value)

        if item['datatype'].startswith('String'):
            value = snap7.util.get_string(data, offset)
            obj.__setattr__(item['name'].replace(" ","_").replace("/","_"), value)

    return obj


def last_byte(data_type, max):

    if data_type == DataTypes.Bool:
        lastByte = int(max) + 1
    elif data_type == DataTypes.Int:
        lastByte = int(max) + 2
    elif data_type == DataTypes.UInt:
        lastByte = int(max) + 2
    elif data_type == DataTypes.Real:
        lastByte = int(max) + 4
    elif data_type == DataTypes.DTime:
        lastByte = int(max) + 4
    elif data_type == DataTypes.DInt:
        lastByte = int(max) + 4
    elif data_type == DataTypes.SInt:
        lastByte = int(max) + 1
    elif data_type == DataTypes.UDInt:
        lastByte = int(max) + 4
    return lastByte


def dbWrite(itemArray): # {data_type, offset, data,stringLength =9999}
    seq,length = [x["offset"] for x in itemArray],[x["data_type"] for x in itemArray]

    maximum = max(seq, key=float)
    minimum = min(seq, key=float)
    size = maximum - minimum

    idx = seq.index(maximum)
    if itemArray[idx]["data_type"] == DataTypes.String:
        lastByte = int(maximum)+item["string_length"]

    else:
        lastByte = last_byte(length[idx], maximum)

    #print("l-m ", lastByte- int(minimum))
    byte_array=bytearray(lastByte-int(minimum))
    
    for item in itemArray:

        if item['data_type'] == DataTypes.Real:
           snap7.util.set_real(byte_array,(int(item["offset"])-int(minimum)),item["data"])

            
        elif item['data_type']== DataTypes.Bool:
                
            bool_index = item["bool_index"]
            snap7.util.set_bool(byte_array,int(item["offset"]-int(minimum)),bool_index,item["data"])

        elif item['data_type']== DataTypes.DInt :
            snap7.util.set_dint(byte_array, int(item["offset"]-int(minimum)), item["data"])


        elif item['data_type']== DataTypes.UDInt:
            snap7.util.set_udint(byte_array, int(item["offset"]-int(minimum)), item["data"])

        elif item['data_type']== DataTypes.Int:
            snap7.util.set_int(byte_array,int(item["offset"]-int(minimum)),item["data"])

        elif item['data_type']== DataTypes.UInt:
            snap7.util.set_uint(byte_array, int(item["offset"]-int(minimum)), item["data"])

        elif item['data_type'] == DataTypes.SInt:
            #snap7.util.set_sint(byte_array,int(item["offset"]-int(minimum)), item["data"])
            byte_array = int(item["data"]).to_bytes(1,'big')


        elif item['data_type']== DataTypes.String:
            str_size = item["string_length"]
            snap7.util.set_string(byte_array, int(item["offset"]-int(minimum)), item["data"], max_size = str_size)

        elif item['data_type'] == DataTypes.DTime:
            snap7.util.set_time(byte_array, int(item["offset"]-int(minimum)), datetime_to_str(item["data"]))
    
    return int(minimum),byte_array,size


def datetime_to_str(dateTime):
    day = rm_firstzero(dateTime.strftime("%d"))
    hour = rm_firstzero(dateTime.strftime("%H"))
    minute = rm_firstzero(dateTime.strftime("%M"))
    second = rm_firstzero(dateTime.strftime("%S"))
    microsec = rm_firstzero(dateTime.strftime("%f"))[0:3]
    return "-" + day + ":" + hour  + ":" + minute  + ":" + second + ":" + microsec

def rm_firstzero(str):
    if str[0] == "0":
        return str[1:]
    else:
        return str

def dbReadArea(plc,area_type, address ,item_data_type,  db_num = 999, bool_index = -1, string_max_size = -1):

    address_integer = int(address)
    address_fraction = (address-address_integer)*10
    value = None

    if area_type == Areas.Input:
        area = snap7.types.S7AreaPE
        offset = address_integer*8 + address_fraction
    elif area_type == Areas.Output:
        area = snap7.types.S7AreaPA
        offset = address_integer*8 + address_fraction
    elif area_type == Areas.Merker:
        area = snap7.types.S7AreaMK
        offset = address_integer*8 + address_fraction

    elif area_type == Areas.DB:
        if db_num == 999:
            print("[Error] : Data Block Number Not Defined. Use Optional Argument db_num.")
            sys.exit()
        area = snap7.types.S7AreaDB
        offset = address

    elif area_type == Areas.Counter:
        area = snap7.types.S7AreaCT
        offset = address_integer*16 + address_fraction

    elif area_type == Areas.Timer:
        area = snap7.types.S7AreaTM
        offset = address_integer*16 + address_fraction


    if item_data_type == DataTypes.Real:
        byte_array = plc.read_area(area,db_num,offset,4)
        value = snap7.util.get_real(byte_array,0)

    if item_data_type == DataTypes.UInt:
        byte_array = plc.read_area(area,db_num,offset,2)
        value = snap7.util.get_uint(byte_array, 0)
        

    elif item_data_type == DataTypes.Bool:
        if bool_index <0 : 
            print("[Error] : Bool Index Not Defined. Use Optional Argument bool_index")
            sys.exit()
        else:
            byte_array = plc.read_area(area,db_num,offset,1)
            value = snap7.util.get_bool(byte_array,0,bool_index)

    elif item_data_type == DataTypes.DInt:

        byte_array = plc.read_area(area,db_num,offset,4)
        value = snap7.util.get_dint(byte_array,0)

    elif item_data_type == DataTypes.UDInt:
        byte_array = plc.read_area(area,db_num,offset,4)
        value=snap7.util.get_udint(byte_array,0)

    elif item_data_type == DataTypes.Int:
        byte_array = plc.read_area(area,db_num,offset,2)
        value = snap7.util.get_int(byte_array,0)

    elif item_data_type == DataTypes.SInt:
        byte_array = plc.read_area(area, db_num, offset, 1)
        value = byte_array[0]

    elif item_data_type == DataTypes.DTime:
        byte_array = plc.read_area(area,db_num,offset,4)
        value = snap7.util.get_time(byte_array,0)
        

    elif item_data_type == DataTypes.String:
        if string_max_size <= 0 :
            print("[Error] : Max String Size Not Defined. Use Optional Argument string_max_size")
            sys.exit()
        else:

            byte_array = plc.read_area(area,db_num,offset,string_max_size)
            value = snap7.util.get_string(byte_array,0,string_max_size)

    return value




def dbWriteArea(plc,area_type, address ,item_data_type, item, db_num = 999, bool_index = -1, string_max_size = -1):

    address_integer = int(address)
    address_fraction = (address-address_integer)*10
    byte_array = None

    if area_type == Areas.Input:
        area = snap7.types.S7AreaPE
        #offset = address_integer*8 + address_fraction
    elif area_type == Areas.Output:
        area = snap7.types.S7AreaPA
        #offset = address_integer*8 + address_fraction
    elif area_type == Areas.Merker:
        area = snap7.types.S7AreaMK
        #offset = address_integer*8 + address_fraction
    elif area_type == Areas.DB:
        if db_num == 1:
            print("[Error] : Data Block Number Not Defined. Use Optional Argument db_num.")
            sys.exit()
        area = snap7.types.S7AreaDB
        #offset = address
    elif area_type == Areas.Counter:
        area = snap7.types.S7AreaCT
        #offset = address_integer*16 + address_fraction
    elif area_type == Areas.Timer:
        area = snap7.types.S7AreaTM
        #offset = address_integer*16 + address_fraction

    
    offset = int(address)
    
    if item_data_type == DataTypes.Real:
        byte_array = bytearray(4)
        snap7.util.set_real(byte_array,0,item)

    elif item_data_type == DataTypes.UInt:
        byte_array = int(item).to_bytes(2,'big')
        snap7.util.set_uint(byte_array,0,item)

    elif item_data_type == DataTypes.Bool:
        if bool_index == 999 : 
            print("[Error] : Bool Index Not Defined. Use Optional Argument bool_index")
            sys.exit()
        else:
            byte_array = plc.read_area(area,db_num,offset,1)
            snap7.util.set_bool(byte_array,0,bool_index,item)

    elif item_data_type == DataTypes.DInt:
        byte_array = bytearray(4)
        snap7.util.set_dint(byte_array,0,item)

    elif item_data_type == DataTypes.UDInt:
        byte_array = bytearray(4)
        snap7.util.set_udint(byte_array,0,item)

    elif item_data_type == DataTypes.SInt:
        byte_array = int(item).to_bytes(1,'big')
        
        
    elif item_data_type == DataTypes.Int:
        byte_array = bytearray(4)
        snap7.util.set_int(byte_array,0,item)


    elif item_data_type == DataTypes.DTime:
        byte_array = bytearray(4)
        snap7.util.set_time(byte_array, 0, datetime_to_str(item))
        
        

    elif item_data_type == DataTypes.String:
        if string_max_size <= 0 :
            print("[Error] : Max String Size Not Defined. Use Optional Argument string_max_size")
            sys.exit()
        else:
            
            StringObj = DTstring()
            byte_array = plc.read_area(area,db_num,offset,string_max_size)

            StringObj.set_string(byte_array,0,item,string_max_size)

    elif item_data_type == DataTypes.Multiple:
        offset,byte_array = dbWrite(plc,item)


    plc.write_area(area,db_num,offset,byte_array)