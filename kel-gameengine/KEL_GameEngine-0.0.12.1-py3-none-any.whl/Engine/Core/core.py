from KEL.Engine.Setup import *
from KEL.Engine.Models.emptyModel import * 
from KEL.Engine.Core.event import *
from KEL.Engine.Core.screen import *

import time

class GameCore:
    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def __init__(self, frameLimit):
        self.clock = pygame.time.Clock()
        self.frameLimit = frameLimit
        self.framerate = 0
        self.coreModules = {'EventHandling': Events(), 'Screen': Screen()}
        self.objects = {}
        self.currentObj = None # The current object in the update loop (yourself when ur component) 
        
        self.materials = {}


        self.inputStateDefault = 'Up'

        self.deltaTime = 0

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def startObjects(self):
        for component in self.objects:
            self.currentObj = self.objects[component]
            self.objects[component].start()


    def startCoreModules(self):
        for module in self.coreModules:
            self.coreModules[module].start()


    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def updateEngine(self):
        # Time
        self.beginTime = time.time()


        for module in self.coreModules:
            self.coreModules[module].updateBefore()
        
        # Updating objects, thats really just updating the blueprint that then updates the components of the object
        for object in self.objects:
            self.currentObj = self.objects[object]
            self.objects[object].update() 

        for module in self.coreModules:
            self.coreModules[module].updateAfter()


        # Time
        self.afterTime = time.time()
        self.deltaTime = self.afterTime - self.beginTime

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def addObject(self, objectName="emptyModel", objectModel=EmptyModel, hitbox=True, components=[], objectLocation='objects') -> None:
        # First get the location by getting the of my self
        location = getattr(self, objectLocation)

        # Then adding it to the attribute
        location[objectName] = objectModel()

        # Then adding the components we might want to add when we create the object
        self.objects[objectName].addComponent(components)

        # Adding a default white material
        self.objects[objectName].material = "#ffffff"

        # Add hitbox bool
        self.objects[objectName].hitbox = hitbox


    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getComponent(self, attribute=''):
        # If nothing is specified return the object u r using
        if attribute == '':
            return self.currentObj
        

        # If it doesnt have the attribute just return the AttributeError 
        try:
            returnValue = self.currentObj.components[attribute]

            return returnValue  

        except AttributeError as err:
            raise err

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getRawComponent(self, object:str, attribute:str=''):
        # So were basicly doing getAttribute function but we specify the object and do not use the currentObj
        if attribute == '':
            return self.objects[object]


        try:
            returnValue = self.objects[object].components[attribute]

            return returnValue

        except AttributeError as err:
            raise err


    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getObject(self):
        return self.currentObj

    def getRawObject(self, object:str):
        return self.objects[object]
    
    def getAllObject(self): # Will not return the obejct your calling from
        returnValue = []
        for obj in self.objects:
            if self.objects[obj] != self.currentObj:
                returnValue.append(self.objects[obj])

        return returnValue
    
    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getAttribute(self, attribute):
        # Get the requested attribute of the current object

        try:
            returnValue = getattr(self.currentObj, attribute)
            return returnValue
        
        except AttributeError as err:
            raise err


    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getRawAttribute(self, object, attribute):
        # Get the requested attribute of the object requested

        try:
            returnValue = getattr(self.objects[object], attribute)
            return returnValue

        except AttributeError as err:
            raise err


    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def Input(self, inputKey, state='Down') -> bool:
        for event in self.coreModules['EventHandling'].events: # Loop thru events list
            if state == "Up":
                if event.type == pygame.KEYUP:
                    if event.key == getattr(pygame, inputKey):
                        return True
                
            elif state == "Down":
                if event.type == pygame.KEYDOWN:
                    if event.key == getattr(pygame, inputKey):
                        return True

        return False


    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def rawInput(self, pygameAttr, eEquals):
        for event in self.coreModules['EventHandling'].events: # Loop thru events list
            attr = getattr(event, pygameAttr)
            equals = getattr(pygame, eEquals)

            if attr == equals:
                return True

        return False

    
    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def createMaterial(self, materialName:str, materialColor:str): # Color will be hexadecimal
        self.materials[materialName] = materialColor

   
    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def addMaterial(self, materialName:str, objectName:str):
        material = self.materials[materialName]
        object = self.objects[objectName]

        object.material = material


    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getMaterial(self) -> str: # This is the material that the current obj has
        return self.currentObj.material

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getRawMaterial(self, materialName):
        return self.materials[materialName]

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getObjectMaterial(self, objectName):
        return self.objects[object].color

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def createFilePreset(self, fileName:str): # This is only experimental
        with open('KEL/Engine/Core/filePreset.py', 'r') as f:
            filePreset = f.read()
            # Returns the index that 'n' is on
            indexN = filePreset.find('name')
            
            filePreset2 = filePreset[:indexN] + fileName + filePreset[indexN+4:]

        with open(fileName + '.py', 'w+') as f:
            f.write(filePreset2)



KEL = GameCore(frameLimit=60)
