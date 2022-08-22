"""
    const
"""

import sys
import tkinter as tk

# device system
if sys.platform == 'win32':
    DEVICE_SYSTEM = 'windows'
elif sys.platform == 'linux':
    DEVICE_SYSTEM = 'linux'
elif sys.platform == 'darwin':
    DEVICE_SYSTEM = 'macos'
else:
    DEVICE_SYSTEM = 'unknown'

# HEIGHT, WIDTH
if DEVICE_SYSTEM == 'windows':
    HEIGHT = tk.Tk().winfo_height()
    WIDTH = tk.Tk().winfo_width()
elif DEVICE_SYSTEM == 'linux' or DEVICE_SYSTEM == 'macos':
    import subprocess
    output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4', shell=True,
                              stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
    HEIGHT = output.split('x')[1]
    WIDTH = output.split('x')[0]
else:
    HEIGHT = -1
    WIDTH = -1
