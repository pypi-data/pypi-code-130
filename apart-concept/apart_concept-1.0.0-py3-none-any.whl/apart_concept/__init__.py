import serial

TIMEOUT = 2


class APartStatus:
    def __init__(self):
        self.source = "A"
        self.musicvolume = 0
        self.standby = False


class APart:
    def __init__(self, url):
        self.url = url
        self.ser = ser = serial.serial_for_url(self.url, do_not_open=True)
        self.ser.baudrate = 19200
        self.ser.timeout = TIMEOUT
        self.ser.open();

    def set_power(self, power: bool):
        if(self.ser.isOpen() == False):
            return(False)
        if power:
            self.ser.write(b'SET STANDBY OFF\r\n')
        else:
            self.ser.write(b'SET STANDBY ON\r\n')
        self.flush()
        return(True)
    
    def set_volume_db(self, volume: float):
        if(self.ser.isOpen() == False):
            return(False)
        cmd = "SET MSCLVL "+str(volume)+"\r\n";
        self.ser.write(bytes(cmd, 'utf-8'))
        self.flush()
        return(True)

    def set_volume(self, volume: int):
        if(self.ser.isOpen() == False):
            return(False)
        value = (volume * 80 / 100) + -80;
        cmd = "SET MSCLVL "+str(int(value))+"\r\n";
        self.ser.write(bytes(cmd, 'utf-8'))
        self.flush()
        return(True)
    
    def set_source(self, source: str):
        if(self.ser.isOpen() == False):
            return(False)
        cmd = "SET SELECT "+source+"\r\n";
        self.ser.write(bytes(cmd, 'utf-8'))
        self.flush()
        return(True)
    
    def set_source_name(self, source: str, sourcename: str):
        if(self.ser.isOpen() == False):
            return(False)
        cmd = "SET SOURCENAME "+source+" "+sourcename+"\r\n";
        self.ser.write(bytes(cmd, 'utf-8'))
        self.flush()
        return(True)
    
    def get_source_name(self, source: str):
        if(self.ser.isOpen() == False):
            return(False)
        # Get a singular sourcename
        self.flush()
        sn = "SOURCENAME "+source;
        cmd = "GET "+sn+"\r";
        self.ser.write(bytes(cmd, 'utf-8'))
        s = self.ser.readline() + self.ser.readline();
        
        arr = s.decode('utf-8').splitlines()
        for val in arr:
            if(val.startswith(sn)):
                return(val.rstrip().replace(sn, "").lstrip())
                break
        return(False)
    
    def get_source_names(self):
        if(self.ser.isOpen() == False):
            return(False)
        # Get all the sourcenames as one list
        sources = ["A", "B", "C", "D"]
        sourcenames = ["a", "b", "c", "d"]
        i = 0;

        for so in sources:
            sourcenames[i] = self.get_source_name(so)
            i = i+1
        
        return(sourcenames)
    
    def get_info(self):
        if(self.ser.isOpen() == False):
            return(False)
        self.flush()
        # Get an Apart Info object
        self.ser.reset_input_buffer()
        self.ser.write(b'GET INFO\r\n')
        s = self.ser.read(1024);
        arr = s.decode('utf-8').splitlines()
        o = APartStatus()

        for val in arr:
            if("STANDBY ON" in val):
                o.standby = True
                break
            if(val.startswith("SELECT")):
                # Selected source
                o.source = val.rstrip().replace("SELECT ", "")
            if(val.startswith("MSCLVL")):
                # Music Volume
                 v = val.rstrip().replace("MSCLVL", "")
                 p = ((int(v) - -80) * 100) / -80;
                 o.musicvolume = abs(int(p))
        return o
        
    def read(self):
        s = self.ser.read(1024)
        #print(s.decode('utf-8'))
        self.ser.close();

    def flush(self):
        # This weird function exists to clear the read buffer as quick as possible
        # Python is a awful language imo and the is no working way to do this so have this hack job instead
        self.ser.timeout = 0.000001
        self.ser.read(1024)
        self.ser.timeout = TIMEOUT


# Example usage
#ap = APart('socket://10.0.2.50:4000');
#ap.set_volume(57)
#ap.set_power(True)
#ap.set_source("A")
#print(ap.get_source_names())
#print(ap.get_source_name("A"))