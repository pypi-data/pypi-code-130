import serial

def defArduino(arduinoport, brate, timeout):
  global arduino
  arduino = serial.Serial(port=arduinoport, baudrate=brate, timeout=timeout)

def writeArduino(msg):
  arduino.write(bytes(msg, 'utf-8'))
  arduino.write(b'\n')

def ewriteArduino(msg):
  arduino.write(bytes(msg, 'utf-8'))