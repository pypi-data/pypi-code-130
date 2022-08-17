from datetime import datetime
import enum

def get_datetime_now():
  return datetime.now().strftime("%Y/%m/%d %H:%M:%S")

class LogType(enum.Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'
    FATAL = 'FATAL'


class LogWriter():
    def __init__(self, filepath, encoding):
        self.debug_num,\
        self.info_num,\
        self.warn_num,\
        self.error_num,\
        self.fatal_num = 0, 0, 0, 0, 0

        self.filepath = filepath
        self.encoding = encoding
        self.create_logfile()

    def create_logfile(self):
        with open(self.filepath, "x", encoding=self.encoding, errors='replace') as f:
            f.write("")
    
    def debug(self, string):
        with open(self.filepath, "a", encoding=self.encoding, errors='replace') as f:
            f.write("DEBUG,%s,%s\n" % (get_datetime_now(), string))
        try:
            print("[DEBUG] - %s\n%s\n" % (get_datetime_now(), string))
        except:
            print("[DEBUG] - %s\n%s\n" % (get_datetime_now(), string.encode('cp932', 'replace')))
        self.debug_num += 1
    
    def info(self, string):
        with open(self.filepath, "a", encoding=self.encoding, errors='replace') as f:
            f.write("INFO,%s,%s\n" % (get_datetime_now(), string))
        try:
            print("[INFO] - %s\n%s\n" % (get_datetime_now(), string))
        except:
            print("[INFO] - %s\n%s\n" % (get_datetime_now(), string.encode('cp932', 'replace')))
        self.info_num += 1
    
    def warn(self, string):
        with open(self.filepath, "a", encoding=self.encoding, errors='replace') as f:
            f.write("WARN,%s,%s\n" % (get_datetime_now(), string))
        try:
            print("[WARN] - %s\n%s\n" % (get_datetime_now(), string))
        except:
            print("[WARN] - %s\n%s\n" % (get_datetime_now(), string.encode('cp932', 'replace')))
        self.warn_num += 1
    
    def error(self, string):
        with open(self.filepath, "a", encoding=self.encoding, errors='replace') as f:
            f.write("ERROR,%s,%s\n" % (get_datetime_now(), string))
        try:
            print("[ERROR] - %s\n%s\n" % (get_datetime_now(), string))
        except:
            print("[ERROR] - %s\n%s\n" % (get_datetime_now(), string.encode('cp932', 'replace')))
        self.error_num += 1
    
    def fatal(self, string):
        with open(self.filepath, "a", encoding=self.encoding, errors='replace') as f:
            f.write("FATAL,%s,%s\n" % (get_datetime_now(), string))
        try:
            print("[FATAL] - %s\n%s\n" % (get_datetime_now(), string))
        except:
            print("[FATAL] - %s\n%s\n" % (get_datetime_now(), string.encode('cp932', 'replace')))
        self.fatal_num += 1

    
def debug(string):
    try:
        print("[DEBUG] - %s\n%s\n" % (get_datetime_now(), string))
    except:
        print("[DEBUG] - %s\n%s\n" % (get_datetime_now(), string.encode('cp932', 'replace')))

def info(string):
    try:
        print("[INFO] - %s\n%s\n" % (get_datetime_now(), string))
    except:
        print("[INFO] - %s\n%s\n" % (get_datetime_now(), string.encode('cp932', 'replace')))

def warn(string):
    try:
        print("[WARN] - %s\n%s\n" % (get_datetime_now(), string))
    except:
        print("[WARN] - %s\n%s\n" % (get_datetime_now(), string.encode('cp932', 'replace')))

def error(string):
    try:
        print("[ERROR] - %s\n%s\n" % (get_datetime_now(), string))
    except:
        print("[ERROR] - %s\n%s\n" % (get_datetime_now(), string.encode('cp932', 'replace')))

def fatal(string):
    try:
        print("[FATAL] - %s\n%s\n" % (get_datetime_now(), string))
    except:
        print("[FATAL] - %s\n%s\n" % (get_datetime_now(), string.encode('cp932', 'replace')))
