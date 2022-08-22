"""
    guto.Position
"""

import pyautogui as ui


class Position(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def click(self):
        ui.moveTo(self.x, self.y, duration=0.5)
        ui.click(self.x, self.y)

    def right_click(self):
        ui.moveTo(self.x, self.y, duration=0.5)
        ui.rightClick(self.x, self.y)

    def doubleclick(self):
        ui.moveTo(self.x, self.y, duration=0.5)
        ui.doubleClick(self.x, self.y)

    def drag_to(self, pos):
        ui.moveTo(self.x, self.y, duration=0.5)
        ui.mouseDown(self.x, self.y)
        ui.moveTo(pos.x, pos.y, duration=0.5)
        ui.mouseUp()

    def show(self):
        pass
