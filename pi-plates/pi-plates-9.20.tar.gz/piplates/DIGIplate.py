import spidev
import time
import site
import sys
import threading
import RPi.GPIO as GPIO
from six.moves import input as raw_input

GPIO.setwarnings(False)

#Initialize
if (sys.version_info < (3,0,0)):
    sys.stderr.write("This library requires Python3")
    exit(1)
    
GPIO.setmode(GPIO.BCM)
DIGIbaseADDR=0x58
ppFRAME = 25
ppACK = 23
ppSRQ=22

GPIO.setup(ppFRAME,GPIO.OUT)
GPIO.output(ppFRAME,False)  #Initialize FRAME signal
time.sleep(.001)            #let Pi-Plate reset SPI engine if necessary
GPIO.setup(ppACK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ppSRQ, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    spi = spidev.SpiDev()
    spi.open(0,1)
except:
    print("Did you enable the SPI hardware interface on your Raspberry Pi?")
    print("Go to https://pi-plates.com/getting_started/ and learn how.")    
    
localPath=site.getsitepackages()[0]
helpPath=localPath+'/piplates/DIGIhelp.txt'
#helpPath='DIGIhelp.txt'       #for development only
DIGIversion=1.0
# Version 1.0   -   initial release

RMAX = 2000
MAXADDR=8
digisPresent = list(range(8))
DataGood=False
lock = threading.Lock()
lock.acquire()

#==============================================================================#
# HELP Functions                                                               #
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
    return DIGIversion

#===============================================================================#   
# Digital Input Functions                                                       #
#===============================================================================#
def getDINbit(addr,bit):
    VerifyADDR(addr)
    VerifyDINchannel(bit-1)
    resp=ppCMD(addr,0x20,bit-1,0,1)
    if resp[0] > 0:
        return 1
    else:
        return 0
        
def getDINall(addr):
    VerifyADDR(addr)
    resp=ppCMD(addr,0x25,0,0,1)
    return resp[0]

#==============================================================================#
# Event Functions                                                              #
#==============================================================================#
def enableDINevent(addr, bit, edge):  # enable DIN interrupt
    VerifyADDR(addr)
    VerifyDINchannel(bit-1)
    bit = bit-1
    if ((edge=='f') or (edge=='F')):
        resp=ppCMD(addr,0x21,bit,0,0)
    if ((edge=='r') or (edge=='R')):
        resp=ppCMD(addr,0x22,bit,0,0)
    if ((edge=='b') or (edge=='B')):
        resp=ppCMD(addr,0x23,bit,0,0)

def disableDINevent(addr,bit):    # disable DIN interrupt
    VerifyADDR(addr)
    VerifyDINchannel(bit-1)
    resp=ppCMD(addr,0x24,bit-1,0,0)    

def eventEnable(addr):    #DIGIplate will pull down on INT pin if an enabled event occurs
    VerifyADDR(addr)
    resp=ppCMD(addr,0x04,0,0,0)

def eventDisable(addr):   #DIGIplate will not assert interrupts
    VerifyADDR(addr)
    resp=ppCMD(addr,0x05,0,0,0)
    
def getEVENTS(addr):  #read INT flag register in DIGIplate - this clears interrupt line and the register
    VerifyADDR(addr)
    resp=ppCMD(addr,0x06,0,0,2)
    value=((resp[0]<<8) + resp[1])
    return value

def check4EVENTS():
    stat=False
    if (GPIO.input(ppSRQ)==0):
        stat=True
    return stat
#==============================================================================#    
# LED Functions                                                                #
#==============================================================================#   
def setLED(addr):
    VerifyADDR(addr)
    resp=ppCMD(addr,0x60,0,0,0)

def clrLED(addr):
    VerifyADDR(addr)
    resp=ppCMD(addr,0x61,0,0,0)

def toggleLED(addr):
    VerifyADDR(addr)
    resp=ppCMD(addr,0x62,0,0,0)
    
#==============================================================================#    
# SYSTEM Functions                                                             #
#==============================================================================#     
def getID(addr):
    global DIGIbaseADDR
    global ppFRAME
    global DataGood
    VerifyADDR(addr)
    addr=addr+DIGIbaseADDR
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
    global DIGIbaseADDR
    VerifyADDR(addr)
    resp=ppCMD(addr,0x02,0,0,1)
    rev = resp[0]
    whole=float(rev>>4)
    point = float(rev&0x0F)
    return whole+point/10.0  
    
def getFWrev(addr):
    global DIGIbaseADDR
    VerifyADDR(addr)
    resp=ppCMD(addr,0x03,0,0,1)
    rev = resp[0]
    whole=float(rev>>4)
    point = float(rev&0x0F)
    return whole+point/10.0

def getVersion():
    return DIGIversion
        
#==============================================================================#    
# LOW Level Functions                                                          #
#==============================================================================#          
def VerifyDINchannel(din):
    assert ((din>=0) and (din<=7)),"Digital input channel value out of range. Must be in the range of 0 to 7"
    
def VerifyADDR(addr):
    assert ((addr>=0) and (addr<MAXADDR)),"DIGIplate address out of range"
    addr_str=str(addr)
    assert (digisPresent[addr]==1),"No DIGIplate found at address "+addr_str


def ppCMD(addr,cmd,param1,param2,bytes2return):
    global DIGIbaseADDR
    global DataGood
    DataGood=True
    arg = list(range(4))
    #resp = []
    resp = [0]*(bytes2return+1)
    arg[0]=addr+DIGIbaseADDR;
    arg[1]=cmd;
    arg[2]=param1;
    arg[3]=param2;
    wait=True
    t0=time.time()
    while(wait):    #ensure that ACK is high before asserting FRAME
        if (GPIO.input(ppACK)!=0):
            wait=False
        if ((time.time()-t0)>0.05):   #timeout
            wait=False
            DataGood=False     
    GPIO.output(ppFRAME,True)       #Set FRAME high - tell Pi-Plates to start listening
    null=spi.xfer(arg,500000,5)     #Send out 4 byte command - ignore what comes back 
    DataGood=True
    t0=time.time()
    wait=True
    while(wait):
        if (GPIO.input(ppACK)!=1):  #wait up to 50msec for the addressed plate to ACKnowledge command
            wait=False
        if ((time.time()-t0)>0.05): #test for timeout
            wait=False
            DataGood=False    
    if (bytes2return>0) and DataGood:   #If plate is supposed to send data AND no timeout occurred
        t0=time.time()
        wait=True
        while(wait):
            if (GPIO.input(ppACK)!=1):  #Ensure that ACK is still low before collecting data             
                wait=False
            if ((time.time()-t0)>0.08): #timeout
                wait=False
                DataGood=False
        if (DataGood==True):            #if ACK is still low AND there was no timeout then fetch data     
            resp=spi.xfer([0]*(bytes2return+1),500000,0)    
            csum=0;                             
            for i in range(0,bytes2return):     #calculate and verify checksum
                csum+=resp[i]
            if ((~resp[bytes2return]& 0xFF) != (csum & 0xFF)):
                DataGood=False
    GPIO.output(ppFRAME,False)
    return resp

def setINT(addr):
    VerifyADDR(addr)
    resp=ppCMD(addr,0xF4,0,0,0)

def clrINT(addr):
    VerifyADDR(addr)
    resp=ppCMD(addr,0xF5,0,0,0)
    
def getADDR(addr):
    global DIGIbaseADDR
    resp = []
    resp=ppCMD(addr,0x00,0,0,1)
    return resp[0]-DIGIbaseADDR

    
def quietPoll():   
    global digisPresent
    ppFoundCount=0
    for i in range (0,8):
        digisPresent[i]=0
        rtn = getADDR(i)
        if (rtn==i):           
            digisPresent[i]=1
            ppFoundCount += 1
            #RESET(i)

def RESET(addr):
    VerifyADDR(addr)
    resp=ppCMD(addr,0x0F,0,0,0)    
    time.sleep(.10)

quietPoll()    
