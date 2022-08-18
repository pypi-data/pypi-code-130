import struct
import snap7
from datetime import datetime
from ctypes import  c_int32
import pdb


class DTtime:
    def __init__(self, readBuffer):
        self.readBuffer = readBuffer


    def db_readTime(self,byteArray,index):
        data=byteArray[index:(index+4)]
        value=struct.unpack('>l' ,struct.pack('4B',*data))[0]
        return value

    def readValue (self,offset):        
        
        result=self.db_readTime(self.readBuffer,offset)
        return result

    def set_dtime(self,dt):

        type_ = c_int32
        buf = bytearray(8)
        buf[0] = dt.second
        buf[1] = dt.minute
        buf[2] = dt.hour
        buf[3] = dt.day
        buf[4] = dt.month - 1
        buf[5] = dt.year - 1900
       
        pdb.set_trace()
        return buf