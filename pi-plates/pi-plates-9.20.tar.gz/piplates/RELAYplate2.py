import spidev
import time
import string
import site
import sys
import threading
from numbers import Number
import RPi.GPIO as GPIO
from six.moves import input as raw_input

GPIO.setwarnings(False)

#Initialize
if (sys.version_info < (3,0,0)):
    sys.stderr.write("You need at least python 2.7.0 to use this library")
    exit(1)
    
GPIO.setmode(GPIO.BCM)
RELAY2baseADDR=0x48
ppFRAME = 25
ppACK = 23

GPIO.setup(ppFRAME,GPIO.OUT)
GPIO.output(ppFRAME,False)  #Initialize FRAME signal
time.sleep(.001)            #let Pi-Plate reset SPI engine if necessary
GPIO.setup(ppACK, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    spi = spidev.SpiDev()
    spi.open(0,1)
except:
    print("Did you enable the SPI hardware interface on your Raspberry Pi?")
    print("Go to https://pi-plates.com/getting_started/ and learn how.")	
    
localPath=site.getsitepackages()[0]
helpPath=localPath+'/piplates/RELAY2help.txt'
#helpPath='RELAY2help.txt'       #for development only
RP2version=1.0
# Version 1.0   -   initial release

RMAX = 2000
MAXADDR=8
relaysPresent = list(range(8))
DataGood=False
lock = threading.Lock()
lock.acquire()

#==============================================================================#
# HELP Functions	                                                           #
#==============================================================================#
def Help():
	help()

def HELP():
	help()	
	
def help():
    valid=True
    try:    
        f=open(helpPath,'r')
        while(valid):
            Count=0
            while (Count<20):
                s=f.readline()
                if (len(s)!=0):
                    print (s[:len(s)-1])
                    Count = Count + 1
                    if (Count==20):
                        Input=raw_input('press \"Enter\" for more...')                        
                else:
                    Count=100
                    valid=False
        f.close()
    except IOError:
        print ("Can't find help file.")

def getSWrev():
    return RP2version


#==============================================================================#
# RELAY Functions	                                                           #
#==============================================================================#
def relayON(addr,relay):
    VerifyADDR(addr)
    VerifyRELAY(relay)
    ppCMDr(addr,0x10,relay-1,0,0)

def relayOFF(addr,relay):
    VerifyADDR(addr)
    VerifyRELAY(relay)
    ppCMDr(addr,0x11,relay-1,0,0)
    
def relayTOGGLE(addr,relay):
    VerifyADDR(addr)
    VerifyRELAY(relay)
    ppCMDr(addr,0x12,relay-1,0,0)   

def relayALL(addr,relays):
    VerifyADDR(addr)
    assert ((relays>=0) and (relays<=255)),"Argument out of range. Must be between 0 and 255"
    ppCMDr(addr,0x13,relays,0,0)     
 
def relaySTATE(addr):
    VerifyADDR(addr)
    resp=ppCMDr(addr,0x14,0,0,1) 
    return resp[0]

#==============================================================================#	
# LED Functions	                                                               #
#==============================================================================#   
def setLED(addr):
    VerifyADDR(addr)
    resp=ppCMDr(addr,0x60,0,0,0)

def clrLED(addr):
    VerifyADDR(addr)
    resp=ppCMDr(addr,0x61,0,0,0)

def toggleLED(addr):
    VerifyADDR(addr)
    resp=ppCMDr(addr,0x62,0,0,0)
    
#==============================================================================#	
# SYSTEM Functions	                                                           #
#==============================================================================#     
def getID(addr):
    global RELAY2baseADDR
    global ppFRAME
    VerifyADDR(addr)
    addr=addr+RELAY2baseADDR
    id=""
    arg = list(range(4))
    resp = []
    arg[0]=addr;
    arg[1]=0x1;
    arg[2]=0;
    arg[3]=0;
    DataGood=True
    wait=True
    t0=time.time()
    while(wait):
        if (GPIO.input(ppACK)==1):
            wait=False
        if ((time.time()-t0)>0.05):   #timeout
            wait=False
            DataGood=False     
    if (DataGood==True):
        GPIO.output(ppFRAME,True)
        time.sleep(0.000001)     #allow the uP some time to initialize the SPI
        null=spi.xfer(arg,500000,5)
        #DataGood=True
        t0=time.time()
        wait=True
        while(wait):
            if (GPIO.input(ppACK)!=1):              
                wait=False
            if ((time.time()-t0)>0.05):   #timeout
                wait=False
                DataGood=False
        if (DataGood==True):
            time.sleep(0.000001)     #allow the uP some time to initialize the SPI
            count=0 
            csum=0
            go=True
            while (go): 
                dummy=spi.xfer([00],500000,5)
                if (dummy[0] != 0):
                    num = dummy[0]
                    csum += num
                    id = id + chr(num)
                    count += 1
                else:
                    dummy=spi.xfer([00],500000,1)  
                    checkSum=dummy[0]                
                    go=False 
                if (count>25):
                    go=False
                    DataGood=False
            if ((~checkSum & 0xFF) != (csum & 0xFF)):
                DataGood=False
        GPIO.output(ppFRAME,False)
        time.sleep(0.000001)     #allow the uP some time to close SPI engine
    return id

def getHWrev(addr):
    global RELAY2baseADDR
    VerifyADDR(addr)
    resp=ppCMDr(addr,0x02,0,0,1)
    rev = resp[0]
    whole=float(rev>>4)
    point = float(rev&0x0F)
    return whole+point/10.0	 
    
def getFWrev(addr):
    global RELAY2baseADDR
    VerifyADDR(addr)
    resp=ppCMDr(addr,0x03,0,0,1)
    rev = resp[0]
    whole=float(rev>>4)
    point = float(rev&0x0F)
    return whole+point/10.0

def getVersion():
    return RP2version      
        
#==============================================================================#	
# LOW Level Functions	                                                       #
#==============================================================================#          
def VerifyRELAY(relay):
    assert ((relay>=1) and (relay<=8)),"Relay number out of range. Must be between 1 and 8"

def VerifyADDR(addr):
    assert ((addr>=0) and (addr<MAXADDR)),"RELAY2plate address out of range"
    addr_str=str(addr)
    assert (relaysPresent[addr]==1),"No RELAY2plate found at address "+addr_str

def ppCMDr(addr,cmd,param1,param2,bytes2return,slow=None):
    global RELAY2baseADDR
    global DataGood
    if (slow==None):
        tOut=0.05
    else:
        tOut=3.0
    arg = list(range(4))
    #resp = []
    resp = [0]*(bytes2return+1)
    #dummy=resp
    arg[0]=addr+RELAY2baseADDR;
    arg[1]=cmd;
    arg[2]=param1;
    arg[3]=param2;
    DataGood=True
    wait=True
    t0=time.time()
    while(wait):
        if (GPIO.input(ppACK)!=0):
            wait=False
        if ((time.time()-t0)>0.05):   #timeout
            wait=False
            DataGood=False 
    GPIO.output(ppFRAME,True)
    time.sleep(0.000001)     #allow the uP some time to initialize the SPI
    null=spi.xfer(arg,400000,0) 
    t0=time.time()
    wait=True
    while(wait):
        if (GPIO.input(ppACK)!=1):
            wait=False
        if ((time.time()-t0)>tOut):   #timeout
            wait=False
            DataGood=False    
    if (bytes2return>0) and DataGood:
        time.sleep(0.000001)     #allow the uP some time to initialize the SPI
        t0=time.time()
        wait=True
        while(wait):
            if (GPIO.input(ppACK)!=1):              
                wait=False
            if ((time.time()-t0)>0.1):   #timeout
                wait=False
                DataGood=False
        if (DataGood==True):
            resp=spi.xfer([0]*(bytes2return+1),400000,0)
            csum=0;
            for i in range(0,bytes2return+1):
                csum+=resp[i]
            if ((csum & 0xFF) != 0xFF):
                DataGood=False
    GPIO.output(ppFRAME,False)
    time.sleep(0.000001)     #allow the uP some time to close SPI engine
    return resp
    
def getADDR(addr):
    global RELAY2baseADDR
    resp = []
    resp=ppCMDr(addr,0x00,0,0,1)
    return resp[0]-RELAY2baseADDR

    
def quietPoll():   
    global relaysPresent
    ppFoundCount=0
    for i in range (0,8):
        relaysPresent[i]=0
        rtn = getADDR(i)
        if (rtn==i):           
            relaysPresent[i]=1
            ppFoundCount += 1
            #RESET(i)

def RESET(addr):
    VerifyADDR(addr)
    resp=ppCMDr(addr,0x0F,0,0,0)    
    time.sleep(.10)

quietPoll()    
