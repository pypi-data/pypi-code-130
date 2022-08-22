"""
    guto.Position
"""

import pyautogui as ui


class Position(object):
    def __init__(self, x, y, duration=0.5):
        self.x = x
        self.y = y
        self.duration = duration

    def click(self):
        ui.moveTo(self.x, self.y, duration=self.duration)
        ui.click(self.x, self.y)

    def right_click(self):
        ui.moveTo(self.x, self.y, duration=self.duration)
        ui.rightClick(self.x, self.y)

    def doubleclick(self):
        ui.moveTo(self.x, self.y, duration=self.duration)
        ui.doubleClick(self.x, self.y)

    def drag_to(self, pos):
        ui.moveTo(self.x, self.y, duration=self.duration)
        ui.mouseDown(self.x, self.y)
        ui.moveTo(pos.x, pos.y, duration=self.duration)
        ui.mouseUp()

    def type(self, msg):
        ui.write(msg)
