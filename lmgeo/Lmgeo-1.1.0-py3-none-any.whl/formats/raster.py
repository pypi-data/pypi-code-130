# Copyright (c) 2004-2020 WUR, Wageningen
from .const import constants as const
import os
from math import sqrt
import pycrs

__author__ = "Steven B. Hoek"

# Abstract base class
class Raster(object):
    # Attributes
    datafile = None
    name = "dummy"
    folder = os.getcwd()
    nodatavalue = -9999.0
    currow = 0
    roty = 0.0
    rotx = 0.0  
    file_exists = False
    
    # Protected attributes
    _mode = 'r'
    _cellsize = 1.0
    _crs = pycrs.parse.from_epsg_code(4326) # default
    
    def __init__(self, filepath):
        self.file_exists = os.path.exists(filepath)

    def open(self, mode, ncols=1, nrows=1, xll=0.0, yll=0.0, cellsize=1.0, nodatavalue=-9999.0):
        # Not all formats support non-square pixels, so initially cellsize represents the horizontal as well as
        # the vertical size of a pixel. After opening, dx and dy may still be set to deviating values if appropriate.
        pass
    
    def readheader(self):
        pass

    def writeheader(self):
        pass
    
    def read_crs(self):
        pass
    
    def __iter__(self):
        if self.datafile is None and self._mode == 'r':
            self.open('r')
        return self; 
    
    def next(self, parseLine=True):
        pass

    def writenext(self, sequence_with_data):
        # input is sequence type - e.g. list, array.array or numpy.array
        pass
    
    @staticmethod
    def getDataFileExt(self):
        result = "xxx"
        if self != None and hasattr(self, "_const"):
            result = self._const.DATAFILEXT
        return result
    
    @staticmethod
    def getHeaderFileExt(self):
        return const.HEADEREXT 
    
    def getWorldFileExt(self):
        return const.WORLDFILEXT   
    
    def close(self):
        try:
            if self.datafile:
                if hasattr(self.datafile, 'closed'):
                    if not self.datafile.closed:
                        self.datafile.close()
                else:
                    self.datafile.close()
        except Exception as e:
            print(e)

    def reset(self):
        self.currow = 0; 

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __next__(self):
        if self._mode == 'r':
            return self.next()
        else:
            raise ValueError("Inappropriate invocation of method __next__!")

    # Raster is often used together with GridEnvelope2D. Here we define cellsize    
    @property
    def cellsize(self):
        if hasattr(self, "_dx") and hasattr(self, "_dy"):
            if (self._dx - self.dy) > const.epsilon:
                return self._cellsize
            else:    
                return sqrt(self._dx * self._dy)
        else:
            return self._cellsize
        
    @cellsize.setter
    def cellsize(self, cellsize):
        self._cellsize = cellsize
        
        
    @property
    def crs(self):
        return self._crs
    
    @crs.setter
    def crs(self, crs):
        if not isinstance(crs, pycrs.CS):
            raise ValueError("Given crs is not an instance of pycrs.CS!")
        else: self._crs = crs