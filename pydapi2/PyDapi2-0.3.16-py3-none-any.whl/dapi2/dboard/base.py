'''Module to define the base class of Dassym's electronic board representation.

:author: F. Voillat
:date: 2021-02-24 Creation
'''

import os
import logging
from enum import IntEnum

from dapi2.dreg.register import Register, RegBit, DRegUndefinedError
from dapi2.dreg.group import RegGroup
from dapi2.dapi2 import DApiAccessLevel, DApiAdditionalBoard
from dapi2.common import versionToWord, dateToWord, wordToDate, wordToVersion, DAPI_ACCESS_LEVEL_MASK
from dapi2.dmsg.message import CommandMessage
from dapi2.signal import DSignal

from .common import DBoardPreferredDapiMode, LastReset, ValueRange, DBoardException, SystemModeConfig
from .workspace import WorkspacesContainer, StandbyWorkspace, Workspace, BaseWorkspace
from .analoginput import PressureSensor, Analog0Sensor, Analog1Sensor, PowerSupply, ReferenceSensor
from .debug import DebugValue



class DacChannel(IntEnum):
    DAC0 = 0
    DAC1 = 1

class DacSignal(IntEnum):
    pass


class WorkspaceChangedSignal(DSignal):
    
    def emit(self, workspace):
        for callback in self.callbacks:
            callback(workspace)    


class ConnectionChangedSignal(DSignal):
    
    def emit(self, state, level):
        for callback in self.callbacks:
            callback(state, level)    

class BaseDBoard(object):
    '''Base class for Dassym electronic boards.
    
    :param DApi2 _dapi: The DAPI2 object.
    :param DBoardPreferredDapiMode dmode: Specifies the preferred DAPI2 operating mode (default: `REGISTER`)
    
    '''
    
    number = '--'
    '''Board type number (str)'''
    
    ext = None
    '''Board type extention (str)'''
     
    wait_after_reprogramming = 8.0 #[s]
    '''Timeout after programming to reconnect to the board expressed in second.'''
    
    wait_after_reboot = 2.0 #[s]
    '''Timeout after reboot to reconnect to the board expressed in second.'''
    
    @classmethod
    def getBoardClasses(cls):
        '''Returns all known board classes
    
        :return: All known board classes
        :rtype: dict 
        '''
        return dict([(c.number,c) for c in cls.__subclasses__()])
    
    @classmethod
    def getSubclasses(cls):
        '''Returns all sub-classes recursively
        
        Returns:
            set: All sub-classes of this class.
        '''
        return set(cls.__subclasses__()).union( [s for c in cls.__subclasses__() for s in c.getSubclasses()])  
    
    @classmethod
    def getName(cls):
        '''Returns the board type name
        :return: The board type name
        :rtype: str
        '''
        if cls.ext is not None:
            return f"MB-{cls.number}-{cls.ext}"
        else:
            return f"MB-{cls.number}"

    @classmethod
    def getCode(cls):
        '''Returns the board type code
        :return: The board type code
        :rtype: str
        '''
        if cls.ext is not None:
            return f"mb{cls.number}{cls.ext.lower()}"
        else:
            return f"mb{cls.number}"

    def __init__(self, dapi, dmode=DBoardPreferredDapiMode.REGISTER):
        '''Constructor'''
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Construct')
        self._dapi = dapi
        self.dmode = dmode
        self._workspace = None
        self._workspaces = WorkspacesContainer(self)
        self._analog_inputs = {}
        self.speed_range = ValueRange(0,40000)
        self.torque_range = ValueRange(0,7000)
        self.powersupply_range = ValueRange(30,36)
        self.analog_input_range = (ValueRange(0,10000),ValueRange(0,10000))
        
        self._workspace_changed = WorkspaceChangedSignal()
        self._connection_changed = ConnectionChangedSignal()
        self._dapi.dcom.connectionChanged.connect(self.onDComConnectionChanged)
        
    def __str__(self):
        return self.getName()
        
    def initialize(self):
        '''Initialize the board object.
        
        The connection with the hardware must be established.
        '''
        self.log.info('Board initialization ...')
        self.log.debug(' - load all undefined registers')
        
        self.refreshAll(undefined_only=True)
        self._workspaces.clear()
        self._workspace = StandbyWorkspace(self)
        self._workspaces.append(self._workspace)
        
        for i in range(self.regs.pcr.size):
            ws_par = i+1
            ws_pcr = self.regs.pcr[i]
            if ws_pcr.value != 0:
                self.log.debug(' - init workspace #{}'.format(ws_par))
                ws = Workspace(self, 'Workspace #'+str(ws_par) , ws_par, ws_pcr)
                self._workspaces.append(ws)
                if self.regs.par.value == ws_par:
                    self.log.debug('- init : Workspace #{} is active'.format(ws_par))
                    self._workspace = ws
        if len(self._workspaces) == 1:
            if self._dapi.dev_mode:
                self.log.warning('No workspace found!')
            else:
                raise DBoardException(self,'initialize', 'No workspace found!')  
            
        
        self._connection_changed.emit(self.dcom.isOpen(), self.getAccessLevel())
        self._workspace_changed.emit(self._workspace)

        self.regs.par.changed.connect(self.onPARChanged)
        self.regs.scsr.changed.connect(self.onSCSRChanged)
            
        self.log.debug('Board initialization is done.')
                    
        
    def setReg(self, reg, value, synchronous=True):
        '''Sets a value to a register.
        
        The modification can be synchronous or not, depending on the `synchronous` parameter.
        If the modification is asynchronous, it is not directly written to the registers of the card.
        The writing will be done the next time the :meth:`DApi2.syncRegs <dapi2.dapi2.DApi2.syncRegs>` method is called.
        If it is synchronous, the modification is directly written in the card registers.
        
        :param reg: The register to be modified
        :type reg: Register, str
        :param int value: The new value
        :param bool synchronous: Specifies whether the modification is synchronous (default) or not.
        '''
        if not isinstance(reg, Register):
            reg = self._dapi.regs.getRegister(reg)
        reg.set(value)
        if synchronous:
            self._dapi.syncRegs()
            #self._dapi.writeReg(reg)
   
            
    def setBit(self, bit, value=1, synchronous=True):
        '''Sets a value to a register's bit.
        
        .. seealso::
            :meth:`setReg`
        
        :param bit: The register's bit to be modified
        :type bit: RegBit, str
        :param int value: The new value (0 or 1). Default 1.
        :param bool synchronous: Specifies whether the modification is synchronous (default) or not.
        '''
        if not isinstance(bit, RegBit):
            bit = self._dapi.getBit(bit)
        if bit.parent.isUndefined() and not self._dapi.dev_mode:
            self._dapi.readReg(bit.parent)
        bit.set(value) 
        if synchronous:
            self._dapi.syncRegs()
            
    def clearBit(self, bit, synchronous=True):
        '''Clear the registers's bit.
        
        .. seealso::
            :meth:`setReg`

        :param bit: The register's bit to be modified
        :type bit: RegBit, str
        :param bool synchronous: Specifies whether the modification is synchronous (default) or not.
        '''
        self.setBit(bit, 0, synchronous)
        
    def toggleBit(self, bit, synchronous=True):
        ''' Toggles the registers's bit.
        
        .. seealso::
            :meth:`setReg`

        :param bit: The register's bit to be modified
        :type bit: RegBit, str
        :param bool synchronous: Specifies whether the modification is synchronous (default) or not.
        '''
        if not isinstance(bit, RegBit):
            bit = self._dapi.getBit(bit)
        bit.parent.alter( bit.toggle() )
        if synchronous:
            self._dapi.syncRegs()

    def setRegs(self, regs, values, synchronous=True):
        '''Sets values to a list of registers.
        
        :param list regs: The registers list to be modified (list of :class:`~dapi2.dmsg.message.BaseMessage`)
        :param int value: The new value
        :param bool synchronous: Specifies whether the modification is synchronous (default) or not. See :meth:`BaseDBoard.setReg` .
        
        '''
        for i, reg in enumerate(regs):
            if not isinstance(reg, Register):
                reg = self._dapi.regs.getRegister(reg)
            reg.alter(values[i])
        if not synchronous:
            self._dapi.syncRegs()
            #self._dapi.writeRegs(regs)
            
    def setRegisters(self, synchronous=False, **regvalues):
        '''Sets values to a list of registers.
        
        :param bool synchronous: Specifies whether the modification is synchronous or not (Default : not = asyncrhonous). See :meth:`BaseDBoard.setReg`
        :param regvalues: Several arguments named according to the name of the registers to be modified.
        '''
        for reg, value in regvalues.items():
            if not isinstance(reg, Register):
                reg = self._dapi.regs.getRegister(reg)
            self.setReg(reg, value, synchronous=False)
        if synchronous:
            self._dapi.syncRegs()

    def getRegisters(self, *registers, refresh=False, undefined_only=False):
        '''Gets values of a list of registers.
        Args:
            regvalues: Several arguments named according to the name of the registers to be modified.
            refresh (bool): True, force read registers form board, else read only undefined registers.
            undefined_only (bool): If True, refresh on only the undefined registers 
        '''
        regs = []
        for reg in registers:
            if not isinstance(reg, Register):
                reg = self._dapi.regs(reg)
            
            if isinstance(reg, RegGroup):
                regs.extend(reg.regs) 
            else:
                regs.append(reg)
        if refresh:
            if undefined_only:
                uregs = [r for r in regs if r.isUndefined()]
                self._dapi.readRegs(*uregs)
            else: 
                self._dapi.readRegs(*regs)
        else:
            uregs = [r for r in regs if r.isUndefined()]
            self._dapi.readRegs(*uregs)
            
        return regs
        

        
    def connect(self, level=DApiAccessLevel.USER, passwd=0x0000):
        '''Connect the *MASTER* to the board.
        
        :param DBoardAccessLevel level: DAPI2 Access level
        :param int passwd: *password* to connect to the board
        
        '''
        if self._dapi.regs.scsr.bits.access.value != DApiAccessLevel.NO.value: #@UndefinedVariable
            self._dapi.cmd.disconnect()
        if level != DApiAccessLevel.NO:
            self._dapi.cmd.connect(level,passwd) 
        try:
            self._dapi.regs.scsr.bits.access.set(level.value)
        except DRegUndefinedError:
            self._dapi.readReg(self._dapi.regs.scsr)
            self._dapi.regs.scsr.bits.access.set(level.value)
        
        
    def setWorkspace(self, workspace):
        '''Sets a new workspace.
        
        :param Workspace workspace: The new workspace to activate.
        :type workspace: BaseWorkspace, int 
        ''' 
        
        if not isinstance(workspace, BaseWorkspace):
            workspace = self.workspaces.getByPAR(workspace)
        if workspace is None:
            raise ValueError('Undefined workspace!')
        if self.dmode == DBoardPreferredDapiMode.COMMAND:
            if workspace.standby:
                self._dapi.cmd.standby()
            else:
                self._dapi.cmd.peripheralActivate(workspace.par)
            self.regs.par.value = workspace.par
        else:
            self.setReg(self._dapi.regs.par, workspace.par)
         
        #self._workspace = workspace
            
    def getWorkspace(self, refresh=False):
        '''Returns the current workspace.
        
        :param bool refresh: specifies whether to update the in-memory register with the one on the board.
        ''' 
        if refresh:
            self._dapi.readReg(self.regs.par)
        if self._workspace is None:
            self.onPARChanged(self.regs.par, self.regs.par.value, self.regs.par.value)
        return self._workspace
            
    def isOnStandby(self):
        '''Check if the board is on standby state.
        
        :return: True, if the board is on standby state ; False otherwise.
        :rtype: bool
        ''' 
        if self._workspace is None:
            self.getWorkspace(refresh=True)
        return self._workspace.standby 
    
    
    def hasBlueLight(self):
        '''Check if the board has the blue light feature.
        
        :return: True, if the board has the blue light feature ; False otherwise.
        :rtype: bool
        ''' 
        try: 
            #self.log.debug('ssr2='+self.regs.ssr2.toString(depth=2))
            return self.regs.ssr2.bits.alt_lmp.value == 1
        except DRegUndefinedError:
            self.getRegisters('ssr2')
            return self.regs.ssr2.bits.alt_lmp.value == 1
        
    def getError(self, refresh=False):
        '''Returns the board error code.
      
        :param bool refresh: Specifies whether to update the in-memory register with the one on the board.
        
        :return: Zero, if the boatrd is'nt in error or warning state : Non-zero, otherwise 
        :rtype: int
        ''' 
        
        if refresh:
            self._dapi.readReg(self.regs.wer)
        return self.regs.wer.value
        
    def getMicrocontrollerID(self):
        
        ret = bytearray(self._dapi.cmd.getMcId(0))
        ret.extend(self._dapi.cmd.getMcId(1))
        return ret
    
    def getLastReset(self, refresh=False):
        if refresh:
            self._dapi.readReg(self.regs.scsr)
        return LastReset(self.regs.scsr.bits.reset.value)

    def getWatchdog(self, refresh=False):
        if refresh:
            self._dapi.readReg(self.regs.scsr)
        return self.regs.scsr.bits.watchdog.value != 0

    
    def getSystemModeConfiguration(self, refresh=False):
        if refresh:
            self._dapi.readReg(self.regs.smr)
        try:
            return SystemModeConfig(self.regs.smr.value)
        except DRegUndefinedError:
            self._dapi.readReg(self.regs.smr)
            return SystemModeConfig(self.regs.smr.value)
        
    def setSystemModeConfiguration(self, flags):
        self.setReg(self.regs.smr, flags.value)
    
    def getAccessLevel(self, refresh=False):
        if refresh or self.regs.scsr.isUndefined():
            self._dapi.readReg(self.regs.scsr)
        return DApiAccessLevel(self.regs.scsr.bits.access.value)
    
    def getAdditionalBoard(self, refresh=False):
        if refresh or self.regs.scsr.isUndefined():
            self._dapi.readReg(self.regs.scsr)
        return DApiAdditionalBoard(self.regs.scsr.bits.ab.value)
    
    def getPowerSupply(self, refresh=False):
        if refresh:
            self._dapi.readReg(self.regs.psvr)
        return self.regs.psvr.value / 1000
    
    def getAnalogInput(self, index, refresh=False):
        reg = self.regs('an{0:d}r'.format(index))
        if refresh: 
            self._dapi.readReg(reg)
        return reg.value
        
    def getSpeedReference(self, refresh=False):
        if refresh: 
            self._dapi.readReg(self.regs.ref)
        return self.regs.ref.value        

    def getPressure(self, refresh=False):
        if refresh: 
            self._dapi.readReg(self.regs.prcr)
        return self.regs.prcr.value        
            
    def getFirmwareVersion(self):
        try:
            return wordToVersion(self.regs.svr.value)
        except DRegUndefinedError:
            self.getRegisters('svr')
            return wordToVersion(self.regs.svr.value)
        
    def getFirmwareDate(self):
        try:
            return wordToDate(self.regs.fbdr.value)
        except DRegUndefinedError:
            self.getRegisters('fbdr')
            return wordToDate(self.regs.fbdr.value)        
        
    
    def getFirmwareTag(self):
        try:
            return self.regs.sctr.value
        except DRegUndefinedError:
            self.getRegisters('sctr')
            return self.regs.sctr.value
     
    def disconnect(self):
        '''Disconnect the *MASTER* from the board.'''
        self._dapi.cmd.disconnect()
        try:
            self._dapi.regs.scsr.bits.access.set(DApiAccessLevel.NO.value)  # @UndefinedVariable
        except DRegUndefinedError:
            self._dapi.readReg(self._dapi.regs.scsr)
            self._dapi.regs.scsr.bits.access.set(DApiAccessLevel.NO.value)  # @UndefinedVariable
        
        
    def reboot(self):
        '''Reboots the board.'''
        self._dapi.cmd.reboot()
        
    def motorStart(self, speed=None ):
        '''Starts the motor and optionally change the speed set point.
        
        :param int speed: The new speed set point. Default no change. 
        ''' 
        if self.dmode == DBoardPreferredDapiMode.COMMAND:
            self._dapi.cmd.motorStart(speed if speed is not None else 0)
        else: 
            if speed is not None:
                self.setReg(self._dapi.regs.scr, speed, synchronous=False)
            self.setBit(self._dapi.regs.smr.start)
            
    def motorStop(self):
        '''Stops the motor.''' 
        if self.dmode == DBoardPreferredDapiMode.COMMAND:
            self._dapi.cmd.motorStop()
        else: 
            self.clearBit(self._dapi.regs.smr.start)
        
    def motorReverse(self, rev=None):
        '''Reverses the direction of rotation of the motor.'''
        if self.dmode == DBoardPreferredDapiMode.COMMAND:
            self._dapi.cmd.motorReverse()
        else: 
            self.toggleBit(self._dapi.regs.smr.reverse)
             
            
    def motorForward(self):
        '''Sets forward direction (clockwise).'''
        self.clearBit(self._dapi.regs.smr.reverse)

    def motorBackward(self):
        '''Sets backward direction (counter clockwise).'''
        self.setBit(self._dapi.regs.smr.reverse)
        
    def memoryStore(self, num):
        '''Stores the current set points into memory..
        
        :param int num: The memory slot number.
        '''
        if self.dmode == DBoardPreferredDapiMode.COMMAND:
            self._dapi.cmd.memoryStore(num)
    
    def memoryRecall(self, num):
        '''Recalls the set points from memory..
        
        :param int num: The memory slot number.
        '''
        if self.dmode == DBoardPreferredDapiMode.COMMAND:
            self._dapi.cmd.memoryRecall(num)
        #self.getRegisters('setpoints')    
               
    def setMotorSpeed(self, speed):
        '''Sets the motor speed
        
        :param int speed: The new motor speed [rpm].
        '''
        self.setReg(self._dapi.regs.scr, speed)
        
    def motorIncSpeed(self, inc):
        '''Increments the motor speed.
        
        :param int inc: The increment value.
        '''
        if self.dmode == DBoardPreferredDapiMode.COMMAND:
            self._dapi.cmd.motorIncSpeed(inc)
        else:
            if self.motorSpeed()+inc > self.speed_range.upper:
                inc = self.speed_range.upper - self.motorSpeed()
            self.setMotorSpeed(self.motorSpeed()+inc)

    def motorDecSpeed(self, inc):
        '''Decrements the motor speed.
        
        :param int inc: The decrement value.
        '''
        if self.dmode == DBoardPreferredDapiMode.COMMAND:
            self._dapi.cmd.motorDecSpeed(inc)
        else:
            if self.motorSpeed()-inc < self.speed_range.lower:
                inc = self.motorSpeed() 
            self.setMotorSpeed(self.motorSpeed()-inc)

    
    def motorSpeed(self):
        '''Returns the motor speed set point'''
        try:
            return self._dapi.regs.scr.value
        except DRegUndefinedError:
            self.getRegisters('scr')
            return self._dapi.regs.scr.value

        
    def motorRealSpeed(self):
        '''Returns the real motor speed'''
        try:
            return self._dapi.regs.msr.value
        except DRegUndefinedError:
            self.getRegisters('msr')
            return self._dapi.regs.msr.value
        
    def setMotorCurrent(self, torque):
        '''Sets the maximum motor current
        
        :param int torque: The new maximum motor current [mA].
        '''
        self.setReg(self._dapi.regs.ccr, torque) 
        
    def motorCurrent(self):
        '''Returns the maximum motor current set point'''
        try:
            return self._dapi.regs.ccr.valued
        except DRegUndefinedError:
            self.getRegisters('ccr')
            return self._dapi.regs.ccr.value
        
    def motorRealCurrent(self):
        '''Returns the real motor current'''
        try:
            return self._dapi.regs.a256dcr.value
        except DRegUndefinedError:
            self.getRegisters('a256dcr')
            return self._dapi.regs.a256dcr.value
    
    def setGearRatio(self, numerator, denominator):
        '''Sets the hand piece gear ratio.
        
        :param int numerator: The numerator (multiplier). 
        :param int denominator: The denominator (divider).
        '''
        self.setRegs(('grnr','grdr'), (numerator, denominator))
        
    def isLightEnabled(self):
        '''Checks if light is enabled.'''
        try:
            return self._dapi.regs.smr.bits.light.value
        except DRegUndefinedError:
            self.getRegisters('smr')
            return self._dapi.regs.smr.bits.light.value

    def isLightAlternate(self):
        '''Checks if the alternate light is activated.'''
        try:
            return self._dapi.regs.alr.value != 0
        except DRegUndefinedError:
            self.getRegisters('alr')
            return self._dapi.regs.alr.value != 0
        
    def isMotorRunning(self):
        '''Checks if motor is running.'''
        try:
            return self._dapi.regs.ssr1.bits.rotation.value
        except DRegUndefinedError:
            self.getRegisters('ssr1')
            return self._dapi.regs.ssr1.bits.rotation.value
    
    def isMotorStarted(self):
        '''Checks if motor is started.'''
        try: 
            return self.regs.smr.bits.start.value == 1
        except DRegUndefinedError:
            self.getRegisters('smr')
            return self.regs.smr.bits.start.value == 1
    

    def isMotorReverse(self):
        '''Checks if CCW direction is selected.'''
        try:
            return self._dapi.regs.smr.bits.reverse.value
        except DRegUndefinedError:
            self.getRegisters('smr')
            return self._dapi.regs.smr.bits.reverse.value

    
    def lightOn(self, on=True):
        '''Enables the light.'''
        if not on:
            self.lightOff()
        else: 
            if self.dmode == DBoardPreferredDapiMode.COMMAND:
                self._dapi.cmd.lightOn()
            else: 
                self.setBit(self._dapi.regs.smr.bits.light)

    def lightOff(self):
        '''Disables the light.'''
        if self.dmode == DBoardPreferredDapiMode.COMMAND:
            self._dapi.cmd.lightOff()
        else: 
            self.clearBit(self._dapi.regs.smr.bits.light)
            
    def lightAuto(self, auto):
        '''Sets the light mode.
        
        :param bool auto: True, sets the automatic mode, False, sets the direct (manual) mode. 
        '''
        self.setBit(self._dapi.regs.smr.bits.lightauto, int(auto))
    

    def lightIntensity(self, intensity):
        '''Sets the light intensity.
        
        :param int intensity: The light intensity in mA'''  
        if self.dmode == DBoardPreferredDapiMode.COMMAND:
            self._dapi.cmd.lightIntensity(intensity)
        else: 
            self.setReg(self._dapi.regs.lir, intensity)

    def lightAlternate(self, alternate=True):
        '''chosen between normal (white) or alternative (UV) light
        
        :param bool alternate: True = Alternate ; False = Normal
        ''' 
        #if self.dmode == DBoardPreferredDapiMode.COMMAND:
        #    self._dapi.cmd.lightAlternate(0x100 * int(alternate))
        #else: 
        self.setReg(self._dapi.regs.alr, 0x100 * int(alternate))

            
    def calibrate(self, part, phase):
        '''Starts calibration procedure
        
        :param int part: Index of part (sensor) to calibrate.
        :param int phase: Pahse number of calibration.   
        '''
        self._dapi.cmd.calibrate(part, phase)
        
    def setFactoryData(self, sn, fd, hv=None):
        '''Sets the factory data.
        
        :param int sn: Serial number.
        :param Date fd: Factory date.
        :param tuple hv: 2-tuple of integer for major and minor version number.
        ''' 
        
        if hv is None:
            hv = wordToVersion(self.regs.hvr.value) 
        
        self.log.info('Set factory data. SN:{0:04d}, FD:{1:s}, HV:{2:d}.{3:02d}'.format(sn, fd.isoformat(), hv[0], hv[1]) )
        
        if self.dmode == DBoardPreferredDapiMode.COMMAND:
            self._dapi.cmd.factSetSysinfo(sn, fd, hv)
        else: 
            self.setRegisters(snr=sn, fdr=dateToWord(fd), hvr = versionToWord(*hv), synchronous=True)        
               
    def getFactoryData(self, read=True):
        '''Returns the factory data.
        
        :return: A 3-tuple containing the serial number (int), the factory date (date) and the hardware version (2-tuple of int). 
        '''
        if read:
            self.getRegisters('snr','fdr','hvr', refresh=True)
        
        return (self.regs.snr.value, wordToDate(self.regs.fdr.value), wordToVersion(self.regs.hvr.value))
        
        
    def refreshAll(self, undefined_only=False):
        self.refreshState(undefined_only=undefined_only)
        self.refreshSetpoints(undefined_only=undefined_only)
        self.refreshDebug(undefined_only=undefined_only)
        self.refreshSystem(undefined_only=undefined_only)
        
    def refreshState(self, part=None, undefined_only=False):
        #self.log.debug('refreshState')
        self.getRegisters('header', refresh=True, undefined_only=undefined_only)
        if part is None:
            self.getRegisters('state', refresh=True, undefined_only=undefined_only)
        else:
            self.getRegisters('ssr1', 'ssr2', 'msr', 'a256dcr', refresh=True, undefined_only=undefined_only)
            if self.regs.ssr1.wanr_err != 0 and part != 8:
                self.getRegisters('wer', refresh=True, undefined_only=undefined_only)
            if part > 0:
                addr = self.regs.state.addr+(part*4) 
                self.getRegisters(self.regs[addr:addr+4], refresh=True, undefined_only=undefined_only)
                

    def refreshSetpoints(self, undefined_only=False):
        #self.log.debug('refreshSetpoints')
        self.getRegisters('setpoints', refresh=True, undefined_only=undefined_only)
        
    def refreshDebug(self, undefined_only=False):
        #self.log.debug('refreshDebug')
        self.getRegisters('debug', refresh=True, undefined_only=undefined_only)

    def refreshAnalogInputs(self, undefined_only=False):
        #self.log.debug('refreshDebug')
        self.getRegisters('prcr', 'elcr', 'an0r', 'an1r', 'psvr', 'esvr',refresh=True, undefined_only=undefined_only)

    def refreshSystem(self, undefined_only=False):
        #self.log.debug('refreshSystem')
        self.getRegisters('system', refresh=True, undefined_only=undefined_only)

        
    def eepromReset(self):
        self._dapi.cmd.factEerpomReset()
        
    def flashFirm(self, firm, callback=None):
        
        def _readByte(x):
            c = f.read(1)
            if c == '':
                return 0
            else:
                return ord(c)
        self.log.info('Firmware programming has started....')
        with open( firm, 'rb' ) as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            self._dapi.cmd.flashBegin(size)
            f.seek(0)
            i = 0
            
            while i < size:
                self._dapi.cmd.flashData([_readByte(x) for x in range(CommandMessage.MAX_DATA_SIZE)])
                i+=CommandMessage.MAX_DATA_SIZE
                self.log.debug('Programming block {0} / {1}'.format(i//CommandMessage.MAX_DATA_SIZE,size//CommandMessage.MAX_DATA_SIZE))
                if callback is not None:
                    callback(i, size)
                    

        self._dapi.cmd.flashEnd()
        self.log.info('Firmware programming is complete!')
        
    def onDComConnectionChanged(self, connected):
        self.log.debug(f'onDComConnectionChanged : {connected}')
        self._connection_changed.emit(connected, self.getAccessLevel())
            
    def onPARChanged(self, reg, old, value):
        self.log.debug('onPARChanged 0x{0:04x} => 0x{1:04x}'.format(old,value))
        self._workspace = self.workspaces.getByPAR(value)
        self.log.info(f'{self._workspace!s} is activated.'.format(old,value))
        self.getRegisters('ctr', refresh=True)
        self._workspace_changed.emit(self._workspace)
        
    def onSCSRChanged(self, reg, old, value):
        self.log.debug('onSCSRChanged 0x{0:04x} => 0x{1:04x}'.format(old,value))
        
        if (old & DAPI_ACCESS_LEVEL_MASK) != (value & DAPI_ACCESS_LEVEL_MASK):
            self._connection_changed.emit(self._dapi.dcom.isOpen(), self.getAccessLevel())
        
    def setDacSignal(self, dac, signal):
        '''Sets the signal that the DAC should generate.
        
        :param dac DacChannel: The DAC channel to change 
        :param signal DacSignal: The signal to set on the DAC channel 
        '''
        assert isinstance(dac, DacChannel) 
        assert isinstance(signal, DacSignal)
        self.setReg(self._dapi.regs.dacsr[dac.value], signal.value, synchronous=True)        
        
    
    @property
    def dapi(self):
        return self._dapi
    @property
    def dcom(self):
        return self._dapi.dcom
    @property
    def regs(self):
        return self._dapi.regs
    @property
    def workspaces(self):
        return self._workspaces
    @property
    def workspace(self):
        return self._workspace
    @property
    def name(self):
        return self.getName().lower()
    @property
    def sn(self):
        return self.regs.snr.value
    @property
    def analogInputs(self):
        return self._analog_inputs.values()
    @property
    def workspaceChanged(self):
        return self._workspace_changed    
    @property
    def connectionChanged(self):
        return self._connection_changed    
    
    
    
class DBoard(BaseDBoard):
    '''Generic class board.
    
    This class is used when the type of card could not be determined.
    
    
    .. inheritance-diagram:: DBoard
        :parts: 1
    
    ''' 
    number = '00'
    '''Board type number'''
    
    DAC_SIGNAL = DacSignal
    
    def __init__(self, dapi, dmode=DBoardPreferredDapiMode.REGISTER):
        BaseDBoard.__init__(self, dapi, dmode=dmode)
        self._analog_inputs = dict( 
                ((sensor.name, sensor) for sensor in (
                    PressureSensor(self),
                    ReferenceSensor(self),
                    Analog0Sensor(self),
                    Analog1Sensor(self), 
                    PowerSupply(self),)
                    )
            )
        self._debug_values = ( DebugValue(self, i) for i in range(self.regs.dmr.size) )
        
        
    @property
    def debugValues(self):
        return self._debug_values