from .__progkids__ import sendCommand


def getDirection():
    return sendCommand('player:getDirection', [])


def getPitch():
    return sendCommand('player:getPitch', [])


def getPos():
    return sendCommand('player:getPos', [])


def getRotation():
    return sendCommand('player:getRotation', [])


def setPos(x, y, z):
    return sendCommand('player:setPos', [x, y, z])


def move(direction, steps):
    return sendCommand('player:move', [direction, steps])


def lookTo(direction):
    return sendCommand('player:lookTo', [direction])


def turnLeft():
    return sendCommand('player:turnLeft', [])


def turnRight():
    return sendCommand('player:turnRight', [])
