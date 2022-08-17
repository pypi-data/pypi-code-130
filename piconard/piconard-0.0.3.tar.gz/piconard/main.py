"""
Create Date : 2021/11/07
Auther :madscientist

Test pypi
command
>poetry config repositories.testpypi https://test.pypi.org/legacy/

"""
import sys
import spidev
from time import sleep
Vref = 3.3

class set_gpio:
    def __init__(self,arg1,arg2):
        self.spi = spidev.SpiDev()
        self.spi.max_speed_hz = 1000000 # 1MHz
        self.A0 = "A0"
        self.A1 = "A1"
        self.A2 = "A2"
        self.A3 = "A3"
        self.A4 = "A4"
        self.A5 = "A5"
        self.D0  = 0
        self.D1  = 1
        self.D2  = 2
        self.D3  = 3
        self.D4  = 4
        self.D5  = 5
        self.D6  = 6
        self.D7  = 7
        self.D8  = 8
        self.D9  = 9
        self.D10 = 10
        self.D11 = 11
        self.D12 = 12
        self.D13 = 13

        if(arg1 == "rpi3" and arg2 == "1.0.0"):
            self.D0  = 15   #D0   = 15
            self.D1  = 14   #D1   = 14
            self.D2  = 17   #D2   = 17
            self.D3  = 18   #D3   = 18
            self.D4  = 27   #D0   = 0
            self.D5  = 22   #D0   = 0
            self.D6  = 23   #D0   = 0
            self.D7  = 24   #D0   = 0
            self.D8  = 25   #D0   = 0
            self.D9  = 4    #D0   = 0
            self.D10 = 8    #D10  = 8 
            self.D11 = 10   #D11  = 10
            self.D12 = 9    #D12  = 9 
            self.D13 = 11   #D13  = 11
    
    def analogRead(self,port):
        if( port == "A0" ):
            port_pin = 0
        elif( port == "A1" ):
            port_pin = 1
        elif( port == "A2" ):
            port_pin = 2
        elif( port == "A3" ):
            port_pin = 3
        elif( port == "A4" ):
            port_pin = 4
        elif( port == "A5" ):
            port_pin = 5
        else:
            print("[Piconard Error] Failure. UNKNOWN PORT PIN NAME ...", file = sys.stderr )
            return
        self.spi.open(port_pin,0) #port 0,cs 0
        adc = self.spi.xfer2([0x06,0x00,0x00])
        data = ((adc[1] & 0x0f) << 8) | adc[2]
        return data
    
    def __del__(self):
        self.spi.close()


