#-*- coding: utf-8 -*-
import snap7
import sys
from EasyS7.Utility import *
from EasyS7.DataBlock import *
from datetime import datetime


class PLC:

    def __init__(self,plc_address , plc_rack , plc_slot , plc_tcpport=102):
        print("[INFO] : Initialization started...")
        self.plc_address = str(plc_address)
        self.plc_rack = int(plc_rack)
        self.plc_slot = int(plc_slot)
        self.plc_tcpport = plc_tcpport
        self.plc = snap7.client.Client()
        self.db_items = None
        self.db_size=None
        print("[INFO] : Initialization done asd...")



    def getDbItems():
        return self.db_items

    def  getDbSize():
        return self.db_size

    def setPlcAdress(plc_address):
        self.plc_address = str(plc_address)

    def setPlcRack(plc_rack):
        self.plc_rack = plc_rack

    def setPlcSlot(plc_slot):
        self.plc_slot = plc_slot

    def setPlcTcpport(plc_tcpport):
        self.plc_tcpport = plc_tcpport

    def disconnect(self):
        print("[INFO] : Closing PLC connection...")
        self.plc.disconnect()
        if not self.plc.get_connected():
                print("[INFO] : Connection closed.")
        else:
                print("[ERROR] : Connection close failed.")
                sys.exit()

    def connect(self):
        print("[INFO] : Establishing PLC connection...")
        try:

            self.plc.connect(self.plc_address,self.plc_rack,self.plc_slot,self.plc_tcpport)
            if self.plc.get_connected():
                print("[INFO] : Connection succeed.")
            else:
                print("[ERROR] : Connection failed.")
                sys.exit()

        except Exception as e:

            print("[ERROR] : ",str(e))
            print("[ERROR] : Connection failed.")
            sys.exit()


    
    def readDb(self,db_no):
            print("[INFO] : Data block read operation started...")
            if self.db_items == None or self.db_size == None:
                print("[ERROR] : Template Info Null, Use readTemplate() First To Fill Template Info")
                sys.exit()
            else:
                db_data = dbRead(self.plc,db_no,self.db_size,self.db_items).__dict__
                print("[INFO] : Data block read operation done...")
                return db_data

    def readTemplate(self, layout_path):
            self.db_items = getItemsFromDbLayout(layout_path)
            self.db_size = getDbSize(self.db_items,'bytebit','datatype')
            

    def writeDb(self, db_items, db_no):
        print("[INFO] : Data block write operation started...")
        if db_items == None or self.db_size == None:
            print("[ERROR] : Template Info Null, Use readTemplate() First To Fill Template Info")
            sys.exit()
        else:
            min, byte_array, size = dbWrite(db_items) 
            self.plc.db_write(db_no, min, byte_array) # just return byte array dont write to plc
            print("[INFO] : Data write operation done...")



    def writeArea(self,area_type, address ,item_data_type, item, db_num = 999, bool_index = -1, string_max_size = -1):
        dbWriteArea(self.plc,area_type, address ,item_data_type, item, db_num,  bool_index , string_max_size )
        #dat = self.plc.read_area(snap7.snap7types.S7AreaDB,101,0,4)
        
    def readArea(self,area_type, address ,item_data_type, db_num = 999, bool_index = -1, string_max_size = -1):
         return dbReadArea(self.plc,area_type, address ,item_data_type, db_num,  bool_index , string_max_size )
        #dat = self.plc.read_area(snap7.snap7types.S7AreaDB,101,0,4)

