from .__progkids__ import sendCommand


class Drone:
    def __init__(self, name):
        self.name = name

    def moveForward(self, distance):
        return sendCommand('drone:moveForward', [self.name, distance])

    def move(self, direction, distance):
        return sendCommand('drone:move', [self.name, direction, distance])

    def lookTo(self, direction):
        return sendCommand('drone:lookTo', [self.name, direction])

    def turn(self):
        return sendCommand('drone:turn', [self.name])

    def turn(self, pitch, yaw):
        return sendCommand('drone:turnLeft', [self.name, pitch, yaw])

    def turnRight(self):
        return sendCommand('drone:turnRight', [self.name])

    def turnLeft(self):
        return sendCommand('drone:turnLeft', [self.name])

    def breakBlock(self):
        return sendCommand('drone:breakBlock', [self.name])

    def placeBlock(self, type):
        return sendCommand('drone:placeBlock', [self.name, type])

    def getBlockInFront(self):
        return sendCommand('drone:getBlockInFront', [self.name])

    def getPos(self):
        return sendCommand('drone:getPos', [self.name])

    def rename(self):
        return sendCommand('drone:rename', [self.name])

    def destroy(self):
        return sendCommand('drone:destroy', [self.name])

    def item(self):
        return sendCommand('drone:item', [self.name])

    def pickItem(self):
        return sendCommand('drone:pickItem', [self.name])

    def putItem(self):
        return sendCommand('drone:putItem', [self.name])

    def takeItem(self, slot, amount, direction):
        return sendCommand('drone:takeItem', [self.name, slot, amount, direction])

    def takeItem(self):
        return sendCommand('drone:takeItem', [self.name])

    def shootArrow(self):
        return sendCommand('drone:shootArrow', [self.name])

    def getInventory(self):
        return sendCommand('drone:getInventory', [self.name])

    def inventoryContains(self, item):
        return sendCommand('drone:inventoryContains', [self.name, item])

    def dropItem(self, material, amount):
        return sendCommand('drone:dropItem', [self.name, material, amount])

    def startDrawing(self):
        return sendCommand('drone:startDrawing', [self.name])

    def setParticle(self, particle):
        return sendCommand('drone:setParticle', [self.name, particle])

    def stopDrawing(self):
        return sendCommand('drone:stopDrawing', [self.name])

    def equip(self, slot):
        return sendCommand('drone:equip', [self.name, slot])

    def unequip(self):
        return sendCommand('drone:unequip', [self.name])


def createDrone(x, y, z, name):
    droneName = sendCommand('drone:createDrone', [x, y, z, name])
    return Drone(droneName)


def removeDrone(name):
    return sendCommand('drone:removeDrone', [name])


def removeAll():
    return sendCommand('drone:removeAll', [])


def getDrone(name):
    drones = sendCommand('drone:list', [])
    if name in drones:
        return Drone(name)
    else:
        print("Дрон {name} не найден".format(name=name))


def list():
    return [Drone(name) for name in sendCommand('drone:list', [])]
