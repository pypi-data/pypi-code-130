import serial
import time

class kiddeejoystick():
    def __init__(self, com_port, baudrate = 115200, timeout = 1):
        self.START = b'\xF1'
        self.STOP = b'\xF2'
        self.buttonUp = None
        self.buttonDown = None
        self.buttonLeft = None
        self.buttonRight = None
        self.buttonX = None
        self.buttonY = None
        self.buttonA = None
        self.buttonB = None
        self.alive = None
        self.timeout = timeout     
        self.ser = None   
        if self.ser != None and self.ser.isOpen():
            try:
                self.ser.close()
            except:
                pass
        try:
            self.ser = serial.Serial(com_port, baudrate, timeout=timeout, writeTimeout=0)
            # self.ser.open()
            self.ser.bytesize = serial.EIGHTBITS
            self.ser.parity = serial.PARITY_NONE
            self.ser.stopbits = serial.STOPBITS_ONE
        except:
            print('Failed to Open COM PORT!\n')
            return
        time.sleep(0.5)
        self.stopJoystick()
        time.sleep(0.5)

    def startJoystick(self):
        currentTime = time.time()
        self.ser.write(self.START)
        while(1):
            c = self.ser.read()
            if time.time()-currentTime > 5:
                print('Failed to connect to Kiddee Joystick after 5 sec! No response.') 
                return
            elif c != b'':
                print('Successly connected to Kiddee Joystick!')
                return
            time.sleep(0.5)
            self.ser.write(self.START)

    def stopJoystick(self):
        self.ser.write(self.STOP)

    def updateJoystick(self): #Would be faster if threading is used
        self.ser.flushInput()
        buff = bytearray()
        count = 0
        for i in range(9):
            c = self.ser.read()
            buff += c
            # print('c:',c)
            count += 1
        # if count != 8:
        #     print('Reading error')
        # print('Data:', buff)
        self.buttonX = int(buff[0])-ord('0')
        self.buttonY = int(buff[1])-ord('0')
        self.buttonA = int(buff[2])-ord('0')
        self.buttonB = int(buff[3])-ord('0')
        self.buttonUp = int(buff[4])-ord('0')
        self.buttonDown = int(buff[5])-ord('0')
        self.buttonLeft = int(buff[6])-ord('0')
        self.buttonRight = int(buff[7])-ord('0')
        self.alive = int(buff[8])-ord('0')

##Usage
# joystick = kiddeejoy(com_port='COM34')
# print('starting!')
# joystick.startJoystick()
# print('reading!')
# joystick.updateJoystick()
# print('stopped!')
# # joystick.stopJoystick()
