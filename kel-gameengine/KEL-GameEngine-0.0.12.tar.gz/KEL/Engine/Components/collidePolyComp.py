from KEL.Engine.Core import *

import math
import random
import numpy


class CollidePolyComp:
    def start(self):
        self.myObj = KEL.currentObj.components['TransformPolyComp']

        self.objects = KEL.getAllObject()

        # See if it has a hitbox
        for i in range(len(self.objects)):
            if self.objects[i].hitbox == False:
                self.objects.pop(i)
    

        # Make it all transformPoly
        for i in range(len(self.objects)):
            self.objects[i] = self.objects[i].components['TransformPolyComp']



        self.collide = False


    def update(self):
        self.objA = KEL.currentObj
        self.updateCorners()

        self.collide = False

        
        # We want to check myObject and all the other objects
        for i in range(len(self.sides)):
            if self.collide == False:
                self.mainLoop(self.mySides, self.myCorners, self.sides[i], self.corners[i])

    def mainLoop(self, mySides, myCorners, objSides, objCorners):
        for mySide in mySides:
            normal = self.normal(mySide)
            scalarsA = [] # First element is p1 and so on
            scalarsB = []
        


            for myCorner in myCorners:
                scalA = self.dotProduct(normal[1], myCorner) # Project corner onto normal (returns a scalar). Tar slutposen med normalen med [0]
                scalarsA.append(scalA)

            for objCorner in objCorners:
                scalB = self.dotProduct(normal[1], objCorner)
                scalarsB.append(scalB)



            # DEBUG:
            # self.printCorners()
            # self.drawNormals(normal, side)


            if self.sortScalar(scalarsA, scalarsB) == False:
                self.collide = False
                break
            else:
                self.collide = True
        
        if self.collide == True:
            for objSide in objSides:
                normal = self.normal(objSide)
                scalarsA = [] # First element is p1 and so on
                scalarsB = []
            

                for myCorner in myCorners:
                    scalA = self.dotProduct(normal[1], myCorner) # Project corner onto normal (returns a scalar). Tar slutposen med normalen med [0]
                    scalarsA.append(scalA)

                for objCorner in objCorners:
                    scalB = self.dotProduct(normal[1], objCorner) # Project corner onto normal (returns a scalar). Tar slutposen av normalen med [0]
                    scalarsB.append(scalB)


                # DEBUG:
                # self.printCorners()
                # self.drawNormals(normal, side)


                if self.sortScalar(scalarsA, scalarsB) == False:
                    self.collide = False
                    break
                else:
                    self.collide = True




    def updateCorners(self):
        # THis is the polyCollide so we know that it will be poly
        self.myCorners = self.myObj.points

        self.mySides = []
        for i in range(len(self.myCorners)):
            if i == len(self.myCorners)-1:
                self.mySides.append([self.myCorners[i], self.myCorners[0]])
            else:
                self.mySides.append([self.myCorners[i], self.myCorners[i+1]])

        self.sides = []
        self.corners = []
        # Loop thru objects
        for object in self.objects:
            try:
                oSide = []

                oCorners = object.points

                for i in range(len(oCorners)):
                    if i == len(oCorners)-1:
                        oSide.append([oCorners[i], oCorners[0]])
                    else:
                        oSide.append([oCorners[i], oCorners[i+1]])

                self.sides.append(oSide)
                self.corners.append(oCorners)

            except:
                # Rect
                pass


    def printCorners(self):
        for corner in self.cornersA:
            pygame.draw.circle(KEL.coreModules['Screen'].wn, (0, 255, 255), corner, 5, 5)

        for corner in self.cornersB:
            pygame.draw.circle(KEL.coreModules['Screen'].wn, (0, 255, 255), corner, 5, 5)


    def drawNormals(self, normal, side):
        p1 = side[0] # p1 is not self.p1, its just the first point of the side
        p2 = side[1]

        # Theta: The angle between xplane and normal
        if normal[1][0] != 0:
            theta = math.radians(math.tan(normal[1][1] / normal[1][0]))
        else:
            # Fix this in the future
            theta = 0


        midX = p1[0] - ((p1[0]-p2[0])/2)
        midY = p1[1] - ((p1[1]-p2[1])/2)

        midPos = [midX, midY]

        bNewNormalX = normal[0][0] + midX
        bNewNormalY = normal[0][1] + midY

        eNewNormalX = normal[1][0] + midX
        eNewNormalY = normal[1][1] + midY

        newNormal = [ [bNewNormalX, bNewNormalY], [eNewNormalX, eNewNormalY] ]

        pygame.draw.circle(KEL.coreModules['Screen'].wn, (255, 0, 0), midPos, 5, 5)

        pygame.draw.line(KEL.coreModules['Screen'].wn, (255, 255, 0), newNormal[0], newNormal[1], 1)


    def drawScalars(normal, scalars):
        pass


    def normal(self, v):
        # Because we didnt input a start pos we will just say that its 
        dx = v[1][0] - v[0][0] # dx= x2 - x1 (slutposx - börjposx) 
        dy = v[1][1] - v[0][1] # dy= y2 - y1 (slutposy - börjposy)
        
        return [[-dy, dx], [dy, -dx]] 



    def dotProduct(self, v1, v2): # Inputed only the end point
        return (v1[0] * v2[0]) + (v1[1] * v2[1])
    

    def sortScalar(self, scalarsA, scalarsB):
        minA = min(scalarsA)
        maxA = max(scalarsA)
        
        minB = min(scalarsB)
        maxB = max(scalarsB)

        if maxA > minB and minA < minB:
            return True
        
        if maxB > minA and minB < minA:
            return True


        return False # No collision
