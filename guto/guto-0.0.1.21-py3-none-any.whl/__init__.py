"""
    guto

    Copyright © 2022 YifeiLiu Authors. All Rights Reserve.

    Licensed under the Apache License, Version 2.0 (the “License”);
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an “AS IS” BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    how to use?
    example:
    ########################################################

    import guto

    start_pos = guto.Position(x=200, y=200)
    end_pos = guto.Position(x=1000, y=1000)
    start_pos.drag_to(pos=end_pos)

    start_pos.click()

    start_pos.doubleclick()

    start_pos.right_click()

    guto.display_realtime_mouse_position()

    ########################################################
"""

import sys
from .position import Position
import pyautogui as ui


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
    import tkinter as tk
    HEIGHT = tk.Tk().winfo_height()
    WIDTH = tk.Tk().winfo_width()
elif DEVICE_SYSTEM == 'linux' or DEVICE_SYSTEM == 'macos':
    import subprocess
    output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4', shell=True,
                              stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
    HEIGHT = output.split('x')[1].replace('\n', '')
    WIDTH = output.split('x')[0].replace('\n', '')
else:
    HEIGHT = -1
    WIDTH = -1


def display_realtime_mouse_position():
    print('you need KeyboardInterrupt to stop capture.')
    try:
        while True:
            x, y = ui.position()
            print('\rx: ' + str(x) + ", y: " + str(y), end='', flush=True)
    except KeyboardInterrupt:
        print("\nstop capture")
