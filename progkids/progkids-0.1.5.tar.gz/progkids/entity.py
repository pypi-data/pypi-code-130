from .__progkids__ import sendCommand


def getDirection(entityID):
    return sendCommand('entity:getDirection', [entityID])


def getPitch(entityID):
    return sendCommand('entity:getPitch', [entityID])


def getPos(entityID):
    return sendCommand('entity:getPos', [entityID])


def getRotation(entityID):
    return sendCommand('entity:getRotation', [entityID])


def setPos(entityID, x, y, z):
    return sendCommand('entity:setPos', [entityID, x, y, z])


def setVelocity(entityID, x, y, z):
    return sendCommand('entity:setVelocity', [entityID, x, y, z])
