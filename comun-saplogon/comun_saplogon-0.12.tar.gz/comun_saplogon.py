import win32com.client
import pyscreeze
import win32gui
from PIL import ImageGrab

import subprocess
import time

SAP_GUI_PATH = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"


class SapGui:

    def __init__(self, nombre_conexion="SAP PRO"):

        self.process = subprocess.Popen(SAP_GUI_PATH)
        time.sleep(10)

        self.SapGuiAuto = win32com.client.GetObject("SAPGUI")
        if not type(self.SapGuiAuto) == win32com.client.CDispatch:
            return

        self.application = self.SapGuiAuto.GetScriptingEngine
        if not type(self.application) == win32com.client.CDispatch:
            self.SapGuiAuto = None
            return

        self.connection = self.application.OpenConnection(nombre_conexion, True)
        if not type(self.connection) == win32com.client.CDispatch:
            self.application = None
            self.SapGuiAuto = None
            return

        if len(self.connection.Children) == 0:
            self.connection.CloseConnection()
            raise Exception('No se encuentra sesión, hay que habilitar scripting')

        self.session = self.connection.Children(0)
        if not type(self.session) == win32com.client.CDispatch:
            self.connection = None
            self.application = None
            self.SapGuiAuto = None
            return

    def login(self, user, password):
        self.session.findById("wnd[0]/usr/txtRSYST-BNAME").text = user
        self.session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = password
        self.session.findById("wnd[0]").sendVKey(0)
        self.session.findById("wnd[0]").maximize()

        if self.session.findById('wnd[1]', False):
            self.session.findById("wnd[1]/usr/radMULTI_LOGON_OPT2").select()
            self.session.findById("wnd[1]/tbar[0]/btn[0]").press()

    def logout(self):
        self.session.findById("wnd[0]").close()
        try:
            self.session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
        except Exception:
            self.session.findById("wnd[2]/usr/btnSPOP-OPTION1").press()

    def close(self):
        self.connection = None
        self.application = None
        self.SapGuiAuto = None
        self.session = None
        self.process.kill()

    def take_screenshot(self, screenshot_name):
        try:
            pyscreeze.screenshot(screenshot_name)
            return True
        except Exception:
            return False

    def save_screenshot(self, screenshot_name):
        try:
            hwnd = win32gui.FindWindowEx(0, 0, 0, self.session.findById("wnd[0]").Text)
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('%')  # evita que salte error en metodo setforegroundwindow
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            bbox = win32gui.GetWindowRect(hwnd)
            img = ImageGrab.grab(bbox)
            img.save(screenshot_name)
            return True
        except Exception:
            return False
