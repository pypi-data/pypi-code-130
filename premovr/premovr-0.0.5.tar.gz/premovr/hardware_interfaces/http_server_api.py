import requests
from typing import Dict

class Board:
    def __init__(self, ip_address: str):
        '''Initialize the board'''
        self.__ip_address = ip_address
    
    def heartbeat(self) -> Dict[str, str]:
        '''Check to see if the board is alive and kickin'''
        r = requests.get('https://xkcd.com/1906/')
        
        pload = {'username':'Olivia','password':'123'}
        r = requests.post('https://httpbin.org/post',data = pload)
        r_dict = r.json()
        return r_dict['form']

    def calibrate(self):
        '''Calibration routines for the board to reset parameters'''
        pass

    def move(self, x: float, y: float):
        '''Move the arm to (x, y)'''
        pass