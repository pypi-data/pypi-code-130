from KEL.Engine.Core import *

import numpy

class TransformPolyComp:
    def __init__(self, points):
        # Make so that u can have many points
        # U might have to update points in update.
        # Make so points are relavant to other points

        # Well do that later
        self.points = points

    def start(self):
        pass

    def update(self):
        pass
    

    def moveX(self, vel):
        for point in self.points:
            point[0] += vel


    def moveY(self, vel):
        for point in self.points:
            point[1] += vel
