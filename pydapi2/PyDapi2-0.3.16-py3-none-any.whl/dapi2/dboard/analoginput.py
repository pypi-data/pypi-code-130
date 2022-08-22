'''

:author: fv
:date: Created on 16 juin 2021
'''
from .common import BaseBoardItem, CalibrationProcessState



class BaseAnalogInput(BaseBoardItem):
    CAL_NEEDED = False
    FMT = '{0:0.0f}%'
    FACTOR = 1/100
    MAX = 100.0
    CAL_INDEX = 0
    REG = None
    NAME = 'unknow'
    def __init__(self, board):
        super().__init__(board, self.NAME)
        self._reg = self.board.regs.getRegister(self.REG)
        self.cal_process_state = CalibrationProcessState.IDLE
    
    def isCalibrated(self):
        return self._board.regs.sfr.value & (1<<(1+self.CAL_INDEX))

    def getRawValue(self, refresh=False):
        if refresh:
            self._board.readReg(self.reg)
        return self._reg.value

    
    def getValue(self, refresh=False):
        return float(self.getRawValue(refresh)) * self.FACTOR
    
    def calibration(self, phase, param=None):
        assert False, 'TODO:calibration'
        
    @property
    def reg(self):
        return self._reg
    @property
    def rawValue(self):
        return self.getRawValue()
    @property
    def value(self):
        return self.getValue()
    
class PressureSensor(BaseAnalogInput):
    NAME = 'Pressure'
    REG = 'prcr'
    CAL_NEEDED = True
    CAL_INDEX = 1
    
class ElectricalSensor(BaseAnalogInput):
    pass

class Analog0Sensor(ElectricalSensor):
    NAME = 'Analog #0'
    REG = 'an0r'

class Analog1Sensor(ElectricalSensor):
    NAME = 'Analog #1'
    REG = 'an1r'

class ReferenceSensor(BaseAnalogInput):
    NAME = 'Reference'
    REG = 'elcr'

class PowerSupply(BaseAnalogInput):
    NAME = 'Power supply'
    FACTOR = 1/1000
    FMT = '{0:0.02f}V'
    MAX = 36.00
    REG = 'psvr'
