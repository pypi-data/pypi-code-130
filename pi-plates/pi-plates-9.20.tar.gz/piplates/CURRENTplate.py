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
CURRENTbaseADDR=0x50
ppFRAME = 25
ppACK = 23
ppSRQ =22

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
helpPath=localPath+'/piplates/CURRENThelp.txt'
#helpPath='CURRENThelp.txt'       #for development only
version=1.0
# Version 1.0   -   initial release

RMAX = 2000
MAXADDR=8
CURRENTPresent = list(range(8))
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
                        raw_input('press \"Enter\" for more...')
                else:
                    Count=100
                    valid=False
        f.close()
    except IOError:
        print ("No help file found.")

def getSWrev():
    return version

#==============================================================================#
# Current Read Functions                                                       #
#==============================================================================#
def getI(addr,channel):
    VerifyADDR(addr)
    VerifyIchannel(channel)
    resp=ppCMD(addr,0x30,channel-1,0,2)
    value=float(256*resp[0]+resp[1])
    value=round((value*24.0/65536.0),4)
    return value

def getIall(addr):
    value=list(range(8))
    VerifyADDR(addr)    
    resp=ppCMD(addr,0x31,0,0,16)
    for i in range (0,8):
        value[i]=float(256*resp[2*i]+resp[2*i+1])
        value[i]=round((value[i]*24.0/65536.0),4)
    return value 


#==============================================================================#
# Unused Precision Functions - analysis showed no clear improvement            #
#==============================================================================#
def initI(addr,channel):
    VerifyADDR(addr)
    VerifyIchannel(channel) 
    ppCMD(addr,0x32,channel-1,0,0)

def initIall(addr):
    VerifyADDR(addr)    
    ppCMD(addr,0x33,0,0,0)   
    
def pullI(addr, channel):
    VerifyADDR(addr)
    VerifyIchannel(channel) 
    resp=ppCMD(addr,0x34,channel-1,0,2)
    value=float(256*resp[0]+resp[1])
    value=round((value*24.0/65536.0),4)
    return value
    
def pullIall(addr):
    value=list(range(8))
    VerifyADDR(addr)    
    resp=ppCMD(addr,0x35,0,0,16)
    for i in range (0,8):
        value[i]=float(256*resp[2*i]+resp[2*i+1])
        value[i]=round((value[i]*24.0/65536.0),4)
    return value 
    
def setFREQ(addr,freq):
    VerifyADDR(addr)
    assert (freq==50 or freq==60), "AC line frequency argument can only be for or 60."
    ppCMD(addr,0x3F,freq,0,0)

#==============================================================================#
# LED Functions                                                                #
#==============================================================================#
def setLED(addr):
    VerifyADDR(addr)
    ppCMD(addr,0x60,0,0,0)

def clrLED(addr):
    VerifyADDR(addr)
    ppCMD(addr,0x61,0,0,0)

def toggleLED(addr):
    VerifyADDR(addr)
    ppCMD(addr,0x62,0,0,0)

#==============================================================================#    
# Interrupt Functions                                                          #
#==============================================================================#    
def intEnable(addr):    #CURRENT will pull down on SRQ pin if an enabled event occurs
    VerifyADDR(addr)
    ppCMD(addr,0x04,0,0,0)

def intDisable(addr):   #CURRENT will not assert SRQ
    VerifyADDR(addr)
    ppCMD(addr,0x05,0,0,0)
    
def getINTflags(addr):  #read SRQ flag register in CURRENT - this clears interrupt line and the register
    VerifyADDR(addr)
    resp=ppCMD(addr,0x06,0,0,1)
    value=(resp[0])
    return value

    
#==============================================================================#    
# Flash Memory Functions - used for calibration constants                      #
#==============================================================================#
def CalGetByte(addr,ptr):
    VerifyADDR(addr)
    assert ((ptr>=0) and (ptr<=255)),"Calibration pointer is out of range. Must be in the range of 0 to 255" 
    resp=ppCMD(addr,0xFD,2,ptr,1)
    return resp[0]
    
def CalPutByte(addr,data):
    VerifyADDR(addr)
    assert ((data>=0) and (data<=255)),"Calibration value is out of range. Must be in the range of 0 to 255"
    ppCMD(addr,0xFD,1,data,0)
    
def CalEraseBlock(addr):
    VerifyADDR(addr)
    ppCMD(addr,0xFD,0,0,0)    
    
#==============================================================================#    
# SYSTEM Functions                                                             #
#==============================================================================#     
def getID(addr):
    global CURRENTbaseADDR
    global ppFRAME
    global DataGood
    VerifyADDR(addr)
    addr=addr+CURRENTbaseADDR
    id=""
    arg = list(range(4))
    #resp = []
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
        spi.xfer(arg,500000,5)
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
    global CURRENTbaseADDR
    VerifyADDR(addr)
    resp=ppCMD(addr,0x02,0,0,1)
    rev = resp[0]
    whole=float(rev>>4)
    point = float(rev&0x0F)
    return whole+point/10.0  
    
def getFWrev(addr):
    global CURRENTbaseADDR
    VerifyADDR(addr)
    resp=ppCMD(addr,0x03,0,0,1)
    rev = resp[0]
    whole=float(rev>>4)
    point = float(rev&0x0F)
    return whole+point/10.0

def getVersion():
    return version      

def setINT(addr):
    VerifyADDR(addr)
    ppCMD(addr,0xF4,0,0,0)

def clrINT(addr):
    VerifyADDR(addr)
    ppCMD(addr,0xF5,0,0,0)
        
#==============================================================================#    
# LOW Level Functions                                                          #
#==============================================================================#          
def VerifyIchannel(Iin):
    assert ((Iin>=1) and (Iin<=8)),"4-20mA input channel value out of range. Must be in the range of 1 to 8" 

def VerifyADDR(addr):
    assert ((addr>=0) and (addr<MAXADDR)),"CURRENTplate address out of range"
    addr_str=str(addr)
    assert (CURRENTPresent[addr]==1),"No CURRENTplate found at address "+addr_str


def ppCMD(addr,cmd,param1,param2,bytes2return):
    global CURRENTbaseADDR
    global DataGood
    DataGood=True
    arg = list(range(4))
    resp = [0]*(bytes2return+1)
    arg[0]=addr+CURRENTbaseADDR;
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
    spi.xfer(arg,500000,5)     #Send out 4 byte command 
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
        if (DataGood):                  #if ACK is low AND there was no timeout then fetch data
            resp=spi.xfer([0]*(bytes2return+1),500000,0)    
            csum=0;                             
            for i in range(0,bytes2return):     #calculate and verify checksum
                csum+=resp[i]
            if ((~resp[bytes2return]& 0xFF) != (csum & 0xFF)):
                DataGood=False
    GPIO.output(ppFRAME,False)
    return resp

    
def getADDR(addr):
    global CURRENTbaseADDR
    #resp = []
    resp=ppCMD(addr,0x00,0,0,1)
    if (DataGood):
        return resp[0]-CURRENTbaseADDR
    else:
        return 8

    
def quietPoll():   
    global CURRENTPresent
    global DataGood
    ppFoundCount=0
    for i in range (0,8):
        CURRENTPresent[i]=0
        rtn = getADDR(i)
        if (rtn==i):           
            CURRENTPresent[i]=1
            ppFoundCount += 1

def RESET(addr):
    VerifyADDR(addr)
    ppCMD(addr,0x0F,0,0,0)    
    time.sleep(1.1)

quietPoll()    
