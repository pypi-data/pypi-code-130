"""
    guto.gui

    a gui tools, to locate mouseinfo
"""


import pyautogui as ui


def run():
    print('you need KeyboardInterrupt to stop capture.')
    try:
        while True:
            x, y = ui.position()
            print('\rx: ' + str(x) + ", y: " + str(y), end='', flush=True)
    except KeyboardInterrupt:
        print("\nstop capture")
