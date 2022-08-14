from KEL.Engine.Setup import *
from KEL.Engine.Core import *


class RenderPolyComp:
    def start(self):
        self.transformComp = KEL.getComponent('TransformPolyComp')

    def update(self):
        self.objectColor = KEL.getMaterial()
        points = self.transformComp.points
        pygame.draw.polygon(KEL.coreModules['Screen'].wn, self.objectColor, points) 
